import * as vscode from "vscode";
import * as http from "http";
import * as cp from "child_process";

let statusBarItem: vscode.StatusBarItem;
let daemonProcess: cp.ChildProcess | undefined;

const DAEMON_PORT = 7777;
const DAEMON_HOST = "127.0.0.1";
const DAEMON_STARTUP_TIMEOUT = 10000; // 10 seconds
const DAEMON_HEALTH_CHECK_INTERVAL = 500; // 500ms

export async function activate(context: vscode.ExtensionContext) {
  vscode.window.showInformationMessage("✓ SpeakLine extension activated");

  // Register commands FIRST
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "speakline.recordAtCursor",
      () => recordAtCursor(false)
    ),
    vscode.commands.registerCommand(
      "speakline.recordAtCursorPreview",
      () => recordAtCursor(true)
    ),
    vscode.commands.registerCommand(
      "speakline.transcribeOnly",
      transcribeOnly
    ),
    vscode.commands.registerCommand(
      "speakline.insertComment",
      insertCommentPrompt
    )
  );

  // Status bar
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100
  );
  statusBarItem.text = "$(mic) SpeakLine";
  statusBarItem.tooltip = "SpeakLine: Click to record comment at cursor";
  statusBarItem.command = "speakline.recordAtCursor";
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  // Start daemon and wait for it
  await startDaemon(context);
}

async function startDaemon(context: vscode.ExtensionContext): Promise<void> {
  vscode.window.showInformationMessage("Starting SpeakLine daemon...");

  try {
    // Get python path and backend from config
    const config = vscode.workspace.getConfiguration("speakline");
    const pythonPath = config.get<string>("pythonPath", "python");
    const backend = config.get<string>("backend", "whisper");

    // Prepare environment with backend setting
    const env = { ...process.env, SPEAKLINE_BACKEND: backend };

    // Spawn daemon process
    daemonProcess = cp.spawn(pythonPath, ["-m", "speakline.daemon", "--port", String(DAEMON_PORT)], {
      detached: true,
      stdio: "ignore",
      env,
    });

    daemonProcess.unref();

    // Wait for daemon to be ready
    await waitForDaemonReady();
    vscode.window.showInformationMessage("✓ SpeakLine daemon ready");
  } catch (err: any) {
    vscode.window.showErrorMessage(
      `✗ Failed to start SpeakLine daemon: ${err.message}`
    );
    throw err;
  }
}

async function waitForDaemonReady(): Promise<void> {
  const startTime = Date.now();

  while (Date.now() - startTime < DAEMON_STARTUP_TIMEOUT) {
    try {
      await sendCommand("/health", {});
      return; // Success
    } catch {
      // Not ready yet, wait and retry
      await new Promise((resolve) =>
        setTimeout(resolve, DAEMON_HEALTH_CHECK_INTERVAL)
      );
    }
  }

  throw new Error(
    `Daemon health check timeout after ${DAEMON_STARTUP_TIMEOUT}ms`
  );
}

async function sendCommand(endpoint: string, body: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const bodyStr = JSON.stringify(body);
    const options = {
      hostname: DAEMON_HOST,
      port: DAEMON_PORT,
      path: endpoint,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(bodyStr),
      },
    };

    const req = http.request(options, (res) => {
      let data = "";

      res.on("data", (chunk) => {
        data += chunk;
      });

      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.ok) {
            resolve(parsed);
          } else {
            reject(new Error(parsed.error || "Unknown daemon error"));
          }
        } catch (err) {
          reject(new Error(`Failed to parse daemon response: ${data}`));
        }
      });
    });

    req.on("error", (err) => {
      reject(err);
    });

    req.write(bodyStr);
    req.end();
  });
}

async function recordAtCursor(preview: boolean) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("SpeakLine: No active editor");
    return;
  }

  const fileUri = editor.document.uri.toString();
  const line = editor.selection.active.line; // 0-indexed

  const config = vscode.workspace.getConfiguration("speakline");
  const duration = config.get<number | null>("recordingDuration", null);

  // Update status bar
  statusBarItem.text = "$(loading~spin) Recording...";
  statusBarItem.backgroundColor = new vscode.ThemeColor(
    "statusBarItem.warningBackground"
  );

  const endpoint = preview ? "/preview" : "/record";

  try {
    const result = await sendCommand(endpoint, {
      file_uri: fileUri,
      line,
      duration,
    });

    if (result.preview) {
      // Show preview in a notification with accept/reject
      const action = await vscode.window.showInformationMessage(
        `Comment: "${result.comment}"`,
        "Insert",
        "Discard"
      );

      if (action === "Insert") {
        await sendCommand("/insert", {
          file_uri: fileUri,
          line,
          comment: result.comment,
        });
        vscode.window.showInformationMessage("Comment inserted!");
        // Reload file to show changes
        await vscode.commands.executeCommand("workbench.action.files.revert");
      }
    } else {
      // Reload the file to show changes
      await vscode.commands.executeCommand("workbench.action.files.revert");
    }
  } catch (err: any) {
    vscode.window.showErrorMessage(`SpeakLine: ${err.message}`);
  } finally {
    // Reset status bar
    statusBarItem.text = "$(mic) SpeakLine";
    statusBarItem.backgroundColor = undefined;
  }
}

async function transcribeOnly() {
  const config = vscode.workspace.getConfiguration("speakline");
  const duration = config.get<number | null>("recordingDuration", null);

  statusBarItem.text = "$(loading~spin) Recording...";

  try {
    const result = await sendCommand("/transcribe", { duration });

    // Copy to clipboard and show
    await vscode.env.clipboard.writeText(result.text);
    vscode.window.showInformationMessage(
      `Transcription (copied to clipboard): "${result.text}"`
    );
  } catch (err: any) {
    vscode.window.showErrorMessage(`SpeakLine: ${err.message}`);
  } finally {
    statusBarItem.text = "$(mic) SpeakLine";
  }
}

async function insertCommentPrompt() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("SpeakLine: No active editor");
    return;
  }

  const comment = await vscode.window.showInputBox({
    prompt: "Enter comment text to insert at cursor",
    placeHolder: "This function calculates the factorial",
  });

  if (!comment) return;

  const fileUri = editor.document.uri.toString();
  const line = editor.selection.active.line;

  try {
    await sendCommand("/insert", {
      file_uri: fileUri,
      line,
      comment,
    });

    await vscode.commands.executeCommand("workbench.action.files.revert");
    vscode.window.showInformationMessage("Comment inserted!");
  } catch (err: any) {
    vscode.window.showErrorMessage(`SpeakLine: ${err.message}`);
  }
}

export function deactivate(): void {
  statusBarItem?.dispose();
  if (daemonProcess) {
    daemonProcess.kill();
  }
}

import * as vscode from "vscode";
import * as path from "path";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
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

  // Start LSP server
  startLanguageServer(context);

  // Register commands
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
}

function startLanguageServer(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("speakline");
  const pythonPath = config.get<string>("pythonPath", "python");
  const lspPort = config.get<number | null>("lspPort", null);

  let serverOptions: ServerOptions;

  if (lspPort) {
    // TCP mode — connect to already-running server
    serverOptions = () => {
      const net = require("net");
      return new Promise((resolve, reject) => {
        const socket = new net.Socket();
        socket.connect(lspPort, "127.0.0.1", () => {
          resolve({ reader: socket, writer: socket });
        });
        socket.on("error", (err: Error) => {
          vscode.window.showErrorMessage(
            `SpeakLine: Cannot connect to LSP server on port ${lspPort}: ${err.message}`
          );
          reject(err);
        });
      });
    };
  } else {
    // stdio mode — spawn the LSP server as a child process
    serverOptions = {
      command: pythonPath,
      args: ["-m", "speakline.lsp"],
      transport: TransportKind.stdio,
    };
  }

  const clientOptions: LanguageClientOptions = {
    documentSelector: [
      { scheme: "file", language: "python" },
      { scheme: "file", language: "javascript" },
      { scheme: "file", language: "typescript" },
      { scheme: "file", language: "go" },
      { scheme: "file", language: "rust" },
      { scheme: "file", language: "java" },
      { scheme: "file", language: "csharp" },
      { scheme: "file", language: "ruby" },
      { scheme: "file", language: "c" },
      { scheme: "file", language: "cpp" },
    ],
  };

  client = new LanguageClient(
    "speakline",
    "SpeakLine Language Server",
    serverOptions,
    clientOptions
  );

  client.start().then(
    () => {
      vscode.window.showInformationMessage("SpeakLine LSP server started");
    },
    (err) => {
      vscode.window.showErrorMessage(
        `SpeakLine: Failed to start LSP server. Ensure 'speakline' is installed: pip install speakline\n${err.message}`
      );
    }
  );

  context.subscriptions.push(client);
}

async function recordAtCursor(preview: boolean) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("SpeakLine: No active editor");
    return;
  }

  if (!client) {
    vscode.window.showErrorMessage("SpeakLine: LSP server not running");
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

  const command = preview
    ? "speakline.recordAtCursorPreview"
    : "speakline.recordAtCursor";

  const args = duration ? [fileUri, line, duration] : [fileUri, line];

  try {
    const result = await client.sendRequest("workspace/executeCommand", {
      command,
      arguments: args,
    });

    if (result && typeof result === "string") {
      const parsed = JSON.parse(result);

      if (parsed.preview) {
        // Show preview in a notification with accept/reject
        const action = await vscode.window.showInformationMessage(
          `Comment: "${parsed.comment}"`,
          "Insert",
          "Discard"
        );

        if (action === "Insert") {
          await client.sendRequest("workspace/executeCommand", {
            command: "speakline.insertComment",
            arguments: [fileUri, line, parsed.comment],
          });
          vscode.window.showInformationMessage("Comment inserted!");
        }
      } else {
        // Reload the file to show changes
        const doc = editor.document;
        if (doc.isDirty) {
          // File was modified externally, need to revert to pick up changes
          await vscode.commands.executeCommand("workbench.action.files.revert");
        }
      }
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
  if (!client) {
    vscode.window.showErrorMessage("SpeakLine: LSP server not running");
    return;
  }

  const config = vscode.workspace.getConfiguration("speakline");
  const duration = config.get<number | null>("recordingDuration", null);

  statusBarItem.text = "$(loading~spin) Recording...";

  try {
    const result = await client.sendRequest("workspace/executeCommand", {
      command: "speakline.transcribeOnly",
      arguments: duration ? [duration] : [],
    });

    if (result && typeof result === "string") {
      const parsed = JSON.parse(result);

      // Copy to clipboard and show
      await vscode.env.clipboard.writeText(parsed.text);
      vscode.window.showInformationMessage(
        `Transcription (copied to clipboard): "${parsed.text}"`
      );
    }
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

  if (!client) {
    vscode.window.showErrorMessage("SpeakLine: LSP server not running");
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
    await client.sendRequest("workspace/executeCommand", {
      command: "speakline.insertComment",
      arguments: [fileUri, line, comment],
    });

    await vscode.commands.executeCommand("workbench.action.files.revert");
    vscode.window.showInformationMessage("Comment inserted!");
  } catch (err: any) {
    vscode.window.showErrorMessage(`SpeakLine: ${err.message}`);
  }
}

export function deactivate(): Thenable<void> | undefined {
  statusBarItem?.dispose();
  if (client) {
    return client.stop();
  }
  return undefined;
}

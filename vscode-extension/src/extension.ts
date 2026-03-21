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

  // Start LSP server and wait for it
  await startLanguageServer(context);
}

function startLanguageServer(context: vscode.ExtensionContext): Promise<void> {
  vscode.window.showInformationMessage("Launching SpeakLine LSP server...");

  const serverOptions: ServerOptions = {
    command: "python",
    args: ["-m", "speakline.lsp"],
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file" }],
  };

  client = new LanguageClient(
    "speakline",
    "SpeakLine Language Server",
    serverOptions,
    clientOptions
  );

  context.subscriptions.push(client);

  return new Promise((resolve, reject) => {
    client!.start().then(
      () => {
        vscode.window.showInformationMessage("✓ SpeakLine LSP initialized");
        resolve();
      },
      (err) => {
        vscode.window.showErrorMessage(`✗ LSP init failed: ${err.message}`);
        reject(err);
      }
    );
  });
}

async function recordAtCursor(preview: boolean) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("SpeakLine: No active editor");
    return;
  }

  if (!client) {
    vscode.window.showErrorMessage(
      "SpeakLine: LSP server failed to start. Ensure 'speakline' is installed: pip install speakline"
    );
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
    vscode.window.showErrorMessage(
      "SpeakLine: LSP server failed to start. Ensure 'speakline' is installed: pip install speakline"
    );
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
    vscode.window.showErrorMessage(
      "SpeakLine: LSP server failed to start. Ensure 'speakline' is installed: pip install speakline"
    );
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

export interface CopilotSessionEndInput {
  sessionId?: string;
  session_id?: string;
  workspacePath?: string;
  workspace_path?: string;
  transcriptPath?: string | null;
  transcript_path?: string | null;
  status?: string;
  error?: string;
}

export interface CopilotSessionEndOutput {
  status: "ok" | "skipped" | "error";
  message?: string;
}

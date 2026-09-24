export interface AntigravityStopHookInput {
  conversationId?: string;
  workspacePaths?: string[];
  transcriptPath?: string | null;
  artifactDirectoryPath?: string;
  modelName?: string;
  executionNum?: number;
  terminationReason?: string;
  error?: string;
  fullyIdle?: boolean;
  loopCount?: number;
  generationId?: string;
  status?: string;
}

export interface AntigravityStopHookOutput {
  decision: "allow" | "continue";
  reason?: string;
}

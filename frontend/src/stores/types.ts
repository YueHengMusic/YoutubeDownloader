export type UiTask = {
  id: string;
  url: string;
  status: "pending" | "running" | "completed" | "failed" | "canceled";
  progress: number;
  speed?: string;
  eta?: string;
  log: string;
  error?: string;
  result_path?: string;
  output_dir: string;
  updated_at: string;
};

export type NoticeType = "success" | "error" | "info";
export type TerminalStreamType = "command" | "stdout" | "status";

export type TerminalLogLine = {
  id: number;
  task_id: string;
  stream: TerminalStreamType;
  text: string;
  created_at: number;
};

export type TaskWsEvent =
  | { type: "task_update"; data: UiTask }
  | { type: "terminal_output"; data: { task_id: string; stream: TerminalStreamType; text: string } };

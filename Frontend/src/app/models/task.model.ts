export interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  type: TaskType;
  assigned_to?: number;
  created_by: number;
  created_at: string;
  updated_at: string;
  due_date?: string;
  completion_percentage: number;
}

export enum TaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum TaskPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

export enum TaskType {
  EMPLOYMENT = 'EMPLOYMENT',
  STUDENT = 'STUDENT',
  BUSINESS = 'BUSINESS',
  CERTIFICATION = 'CERTIFICATION'
}

export interface CreateTask {
  title: string;
  description: string;
  priority: TaskPriority;
  type: TaskType;
  assigned_to?: number;
  due_date?: string;
}

export interface UpdateTask {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigned_to?: number;
  due_date?: string;
  completion_percentage?: number;
}

export interface TaskStats {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
  cancelled: number;
}

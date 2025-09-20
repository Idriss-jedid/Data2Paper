import { Component, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../../auth/auth.service';
import { TaskService } from '../../services/task.service';
import { User, UserRole } from '../../models/user.model';
import { Task, TaskStats, TaskStatus, TaskPriority, TaskType, CreateTask } from '../../models/task.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit, OnDestroy {
  currentUser: User | null = null;
  allTasks: Task[] = [];
  taskStats: TaskStats | null = null;
  allUsers: User[] = [];
  isLoading = true;
  private destroy$ = new Subject<void>();

  // Expose enums to template
  TaskStatus = TaskStatus;
  TaskPriority = TaskPriority;
  TaskType = TaskType;

  // Chart data
  taskStatusData: any[] = [];
  taskPriorityData: any[] = [];
  taskTypeData: any[] = [];

  // Quick stats
  totalUsers = 0;
  activeUsers = 0;
  totalTasks = 0;
  completedTasks = 0;
  pendingTasks = 0;
  overdueTasks = 0;

  // Recent activity
  recentTasks: Task[] = [];
  recentUsers: User[] = [];

  // Task creation form
  showCreateTaskForm = false;
  newTask: CreateTask = {
    title: '',
    description: '',
    priority: TaskPriority.MEDIUM,
    type: 'BUSINESS' as any,
    assigned_to: undefined,
    due_date: undefined
  };

  constructor(
    private authService: AuthService,
    private taskService: TaskService
  ) {}

  ngOnInit(): void {
    this.loadAdminData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadAdminData(): void {
    this.loadUserData();
    this.loadAllTasks();
    this.loadTaskStats();
    // In a real app, you'd have a user service to load all users
    this.loadUsers();
  }

  private loadUserData(): void {
    this.authService.user$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => {
        this.currentUser = user;
      });
  }

  private loadAllTasks(): void {
    this.taskService.getTasks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tasks) => {
          this.allTasks = tasks;
          this.recentTasks = tasks.slice(0, 5);
          this.calculateTaskStats();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading tasks:', error);
          this.isLoading = false;
        }
      });
  }

  private loadTaskStats(): void {
    this.taskService.getTaskStats()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats) => {
          this.taskStats = stats;
          this.prepareChartData();
        },
        error: (error) => {
          console.error('Error loading task stats:', error);
        }
      });
  }

  private loadUsers(): void {
    // This would be replaced with actual user service call
    this.allUsers = [
      { id: 1, name: 'John Doe', email: 'john@example.com', role: UserRole.USER, is_active: true },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: UserRole.MANAGER, is_active: true },
      { id: 3, name: 'Bob Wilson', email: 'bob@example.com', role: UserRole.USER, is_active: false }
    ];
    
    this.totalUsers = this.allUsers.length;
    this.activeUsers = this.allUsers.filter(user => user.is_active).length;
    this.recentUsers = this.allUsers.slice(0, 3);
  }

  private calculateTaskStats(): void {
    this.totalTasks = this.allTasks.length;
    this.completedTasks = this.allTasks.filter(task => task.status === TaskStatus.COMPLETED).length;
    this.pendingTasks = this.allTasks.filter(task => task.status === TaskStatus.PENDING).length;
    
    const today = new Date();
    this.overdueTasks = this.allTasks.filter(task => {
      const dueDate = task.due_date ? new Date(task.due_date) : null;
      return dueDate && dueDate < today && task.status !== TaskStatus.COMPLETED;
    }).length;
  }

  private prepareChartData(): void {
    if (!this.taskStats) return;

    this.taskStatusData = [
      { name: 'Pending', value: this.taskStats.pending, color: '#ff9500' },
      { name: 'In Progress', value: this.taskStats.in_progress, color: '#007aff' },
      { name: 'Completed', value: this.taskStats.completed, color: '#34c759' },
      { name: 'Cancelled', value: this.taskStats.cancelled, color: '#ff3b30' }
    ];

    // Task priority distribution
    const priorityCount = this.allTasks.reduce((acc, task) => {
      acc[task.priority] = (acc[task.priority] || 0) + 1;
      return acc;
    }, {} as any);

    this.taskPriorityData = [
      { name: 'Low', value: priorityCount[TaskPriority.LOW] || 0, color: '#34c759' },
      { name: 'Medium', value: priorityCount[TaskPriority.MEDIUM] || 0, color: '#ffcc00' },
      { name: 'High', value: priorityCount[TaskPriority.HIGH] || 0, color: '#ff9500' },
      { name: 'Urgent', value: priorityCount[TaskPriority.URGENT] || 0, color: '#ff3b30' }
    ];

    // Task type distribution
    const typeCount = this.allTasks.reduce((acc, task) => {
      acc[task.type] = (acc[task.type] || 0) + 1;
      return acc;
    }, {} as any);

    this.taskTypeData = Object.keys(typeCount).map(type => ({
      name: type,
      value: typeCount[type],
      color: this.getTaskTypeColor(type)
    }));
  }

  getTaskStatusColor(status: TaskStatus): string {
    switch (status) {
      case TaskStatus.COMPLETED: return '#34c759';
      case TaskStatus.IN_PROGRESS: return '#007aff';
      case TaskStatus.PENDING: return '#ff9500';
      case TaskStatus.CANCELLED: return '#ff3b30';
      default: return '#8e8e93';
    }
  }

  getTaskPriorityColor(priority: TaskPriority): string {
    switch (priority) {
      case TaskPriority.URGENT: return '#ff3b30';
      case TaskPriority.HIGH: return '#ff9500';
      case TaskPriority.MEDIUM: return '#ffcc00';
      case TaskPriority.LOW: return '#34c759';
      default: return '#8e8e93';
    }
  }

  getTaskTypeColor(type: string): string {
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
    const index = type.charCodeAt(0) % colors.length;
    return colors[index];
  }

  getUserRoleColor(role: UserRole): string {
    switch (role) {
      case UserRole.ADMIN: return '#ff3b30';
      case UserRole.MANAGER: return '#ff9500';
      case UserRole.USER: return '#007aff';
      default: return '#8e8e93';
    }
  }

  getUserStatusColor(isActive: boolean): string {
    return isActive ? '#34c759' : '#8e8e93';
  }

  updateTaskStatus(taskId: number, status: TaskStatus): void {
    this.taskService.updateTask(taskId, { status })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadAllTasks();
          this.loadTaskStats();
        },
        error: (error) => {
          console.error('Error updating task status:', error);
        }
      });
  }

  assignTask(taskId: number, userId: number): void {
    this.taskService.assignTask(taskId, userId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadAllTasks();
        },
        error: (error) => {
          console.error('Error assigning task:', error);
        }
      });
  }

  createTask(): void {
    if (!this.newTask.title || !this.newTask.description) return;

    this.taskService.createTask(this.newTask)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadAllTasks();
          this.loadTaskStats();
          this.resetTaskForm();
          this.showCreateTaskForm = false;
        },
        error: (error) => {
          console.error('Error creating task:', error);
        }
      });
  }

  resetTaskForm(): void {
    this.newTask = {
      title: '',
      description: '',
      priority: TaskPriority.MEDIUM,
      type: 'BUSINESS' as any,
      assigned_to: undefined,
      due_date: undefined
    };
  }

  deleteTask(taskId: number): void {
    if (confirm('Are you sure you want to delete this task?')) {
      this.taskService.deleteTask(taskId)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.loadAllTasks();
            this.loadTaskStats();
          },
          error: (error) => {
            console.error('Error deleting task:', error);
          }
        });
    }
  }

  logout(): void {
    this.authService.logout();
  }

  refreshData(): void {
    this.isLoading = true;
    this.loadAdminData();
  }
}

import { Component, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../../auth/auth.service';
import { TaskService } from '../../services/task.service';
import { User, UserRole } from '../../models/user.model';
import { Task, TaskStats, TaskStatus, TaskPriority } from '../../models/task.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-user-dashboard',
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.scss']
})
export class UserDashboardComponent implements OnInit, OnDestroy {
  currentUser: User | null = null;
  userTasks: Task[] = [];
  taskStats: TaskStats | null = null;
  isLoading = true;
  private destroy$ = new Subject<void>();

  // Expose enums to template
  TaskStatus = TaskStatus;
  TaskPriority = TaskPriority;

  // Chart data
  taskStatusData: any[] = [];
  taskPriorityData: any[] = [];

  // Quick stats
  todayTasks = 0;
  overdueTasks = 0;
  completedThisWeek = 0;

  constructor(
    private authService: AuthService,
    private taskService: TaskService
  ) {}

  ngOnInit(): void {
    this.loadUserData();
    this.loadUserTasks();
    this.loadTaskStats();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadUserData(): void {
    this.authService.user$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => {
        this.currentUser = user;
      });
  }

  private loadUserTasks(): void {
    this.taskService.getUserTasks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tasks) => {
          this.userTasks = tasks;
          this.calculateQuickStats();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading user tasks:', error);
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

  private calculateQuickStats(): void {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    this.todayTasks = this.userTasks.filter(task => {
      const dueDate = task.due_date ? new Date(task.due_date) : null;
      return dueDate && dueDate.getTime() === today.getTime();
    }).length;

    this.overdueTasks = this.userTasks.filter(task => {
      const dueDate = task.due_date ? new Date(task.due_date) : null;
      return dueDate && dueDate < today && task.status !== TaskStatus.COMPLETED;
    }).length;

    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 7);
    
    this.completedThisWeek = this.userTasks.filter(task => {
      const updatedDate = new Date(task.updated_at);
      return task.status === TaskStatus.COMPLETED && updatedDate >= weekAgo;
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

  getTaskPriorityIcon(priority: TaskPriority): string {
    switch (priority) {
      case TaskPriority.URGENT: return 'priority_high';
      case TaskPriority.HIGH: return 'keyboard_arrow_up';
      case TaskPriority.MEDIUM: return 'remove';
      case TaskPriority.LOW: return 'keyboard_arrow_down';
      default: return 'remove';
    }
  }

  getProgressColor(percentage: number): string {
    if (percentage >= 80) return '#34c759';
    if (percentage >= 50) return '#ffcc00';
    if (percentage >= 25) return '#ff9500';
    return '#ff3b30';
  }

  updateTaskStatus(taskId: number, status: TaskStatus): void {
    this.taskService.updateTask(taskId, { status })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadUserTasks();
          this.loadTaskStats();
        },
        error: (error) => {
          console.error('Error updating task status:', error);
        }
      });
  }

  logout(): void {
    this.authService.logout();
  }

  refreshData(): void {
    this.isLoading = true;
    this.loadUserTasks();
    this.loadTaskStats();
  }
}

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { Task, CreateTask, UpdateTask, TaskStats } from '../models/task.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private apiUrl = `${environment.apiUrl}/tasks`;
  private tasksSubject = new BehaviorSubject<Task[]>([]);
  public tasks$ = this.tasksSubject.asObservable();

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // Get all tasks
  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(this.apiUrl, { headers: this.getAuthHeaders() });
  }

  // Get user's tasks
  getUserTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.apiUrl}/my-tasks`, { headers: this.getAuthHeaders() });
  }

  // Get task by ID
  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Create new task
  createTask(task: CreateTask): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, task, { headers: this.getAuthHeaders() });
  }

  // Update task
  updateTask(id: number, task: UpdateTask): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${id}`, task, { headers: this.getAuthHeaders() });
  }

  // Delete task
  deleteTask(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Get task statistics
  getTaskStats(): Observable<TaskStats> {
    return this.http.get<TaskStats>(`${this.apiUrl}/stats`, { headers: this.getAuthHeaders() });
  }

  // Assign task to user
  assignTask(taskId: number, userId: number): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${taskId}/assign/${userId}`, {}, { headers: this.getAuthHeaders() });
  }

  // Load and cache tasks
  loadTasks(): void {
    this.getTasks().subscribe(tasks => {
      this.tasksSubject.next(tasks);
    });
  }

  // Load user tasks and cache
  loadUserTasks(): void {
    this.getUserTasks().subscribe(tasks => {
      this.tasksSubject.next(tasks);
    });
  }
}

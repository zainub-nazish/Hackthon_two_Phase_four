/**
 * Component Contracts: Frontend Application
 *
 * This file defines the TypeScript interfaces for UI components.
 * These contracts ensure consistent props across the application.
 *
 * Feature: 003-frontend-app
 * Date: 2026-01-13
 */

import type { Task, TaskCreate, TaskUpdate } from './api-client';

// =============================================================================
// Common Props
// =============================================================================

export interface BaseProps {
  className?: string;
}

// =============================================================================
// Auth Components
// =============================================================================

export interface LoginFormProps extends BaseProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

export interface LogoutButtonProps extends BaseProps {
  onLogout?: () => void;
}

export interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

// =============================================================================
// Task Components
// =============================================================================

export interface TaskListProps extends BaseProps {
  tasks: Task[];
  isLoading?: boolean;
  onToggleComplete: (taskId: string, completed: boolean) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

export interface TaskItemProps extends BaseProps {
  task: Task;
  onToggleComplete: (completed: boolean) => void;
  onEdit: () => void;
  onDelete: () => void;
  isUpdating?: boolean;
}

export interface TaskFormProps extends BaseProps {
  initialData?: Partial<TaskCreate>;
  onSubmit: (data: TaskCreate) => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

export interface TaskEditFormProps extends BaseProps {
  task: Task;
  onSubmit: (data: TaskUpdate) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export interface TaskFilterProps extends BaseProps {
  currentFilter: 'all' | 'pending' | 'completed';
  onFilterChange: (filter: 'all' | 'pending' | 'completed') => void;
  counts: {
    all: number;
    pending: number;
    completed: number;
  };
}

// =============================================================================
// UI Components
// =============================================================================

export interface ButtonProps extends BaseProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: () => void;
  children: React.ReactNode;
}

export interface InputProps extends BaseProps {
  label?: string;
  error?: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password';
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
}

export interface TextareaProps extends BaseProps {
  label?: string;
  error?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  rows?: number;
}

export interface CheckboxProps extends BaseProps {
  label?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export interface ModalProps extends BaseProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export interface ConfirmDialogProps extends BaseProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  isConfirming?: boolean;
}

// =============================================================================
// Feedback Components
// =============================================================================

export interface ToastProps extends BaseProps {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  onDismiss?: () => void;
  duration?: number;
}

export interface SkeletonProps extends BaseProps {
  variant?: 'text' | 'rectangular' | 'circular';
  width?: string | number;
  height?: string | number;
}

export interface EmptyStateProps extends BaseProps {
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
}

export interface ErrorStateProps extends BaseProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

// =============================================================================
// Layout Components
// =============================================================================

export interface HeaderProps extends BaseProps {
  user?: { id: string; email?: string };
  onLogout: () => void;
}

export interface SidebarProps extends BaseProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export interface PageContainerProps extends BaseProps {
  title?: string;
  children: React.ReactNode;
}

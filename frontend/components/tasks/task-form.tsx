"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Task, TaskCreate, TaskUpdate } from "@/types";

interface TaskFormProps {
  initialData?: Task;
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function TaskForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditing = !!initialData;

  function validate(): boolean {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = "Title is required";
    } else if (title.length > 255) {
      newErrors.title = "Title must be 255 characters or less";
    }

    if (description && description.length > 2000) {
      newErrors.description = "Description must be 2000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const data: TaskCreate | TaskUpdate = {
      title: title.trim(),
      description: description.trim() || undefined,
    };

    await onSubmit(data);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter task title"
        required
        disabled={isLoading}
        error={errors.title}
        autoFocus
      />

      <div className="w-full">
        <label
          htmlFor="description"
          className="mb-1.5 block text-sm font-medium text-light"
        >
          Description (optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add a description..."
          rows={3}
          disabled={isLoading}
          className="flex w-full rounded-md border border-white/20 bg-surface px-3 py-2 text-sm text-light placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-dark resize-none"
        />
        {errors.description && (
          <p className="mt-1.5 text-sm text-danger">{errors.description}</p>
        )}
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {isEditing ? "Save changes" : "Add task"}
        </Button>
      </div>
    </form>
  );
}

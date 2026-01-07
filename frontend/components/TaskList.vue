<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import { Icon } from "@iconify/vue";

const API_URL = import.meta.env.PROD
  ? "/api/tasks"
  : "http://localhost:8000/tasks";

const tasks = ref([]);
const isLoading = ref(false);
const error = ref(null);

// Form state
const formData = ref({
  id: null,
  title: "",
  priority: 3,
  due_date: "",
});
const isEditing = ref(false);
const filterStatus = ref("all"); // all, pending, completed
const sortBy = ref("priority"); // priority, due_date

const priorityLabels = {
  1: "High",
  2: "Medium",
  3: "Low",
};

const priorityClasses = {
  1: "priority-high",
  2: "priority-medium",
  3: "priority-low",
};

// Fetch tasks
const fetchTasks = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(API_URL);
    tasks.value = response.data;
  } catch (err) {
    error.value = "Failed to load tasks";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

// Add or Update Task
const handleSubmit = async () => {
  if (!formData.value.title.trim()) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Title cannot be empty!",
    });
    return;
  }

  try {
    if (isEditing.value) {
      await axios.put(`${API_URL}/${formData.value.id}`, formData.value);
    } else {
      await axios.post(API_URL, formData.value);
    }

    // Reset form and refresh list
    resetForm();
    await fetchTasks();
    Swal.fire({
      icon: "success",
      title: isEditing.value ? "Task Updated" : "Task Added",
      showConfirmButton: false,
      timer: 1500,
    });
  } catch (err) {
    Swal.fire({
      icon: "error",
      title: "Operation Failed",
      text: err.response?.data?.error || "Something went wrong",
    });
    console.error(err);
  }
};

// Delete Task
const deleteTask = async (id) => {
  const result = await Swal.fire({
    title: "Are you sure?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Yes, delete it!",
  });

  if (!result.isConfirmed) return;

  try {
    await axios.delete(`${API_URL}/${id}`);
    await fetchTasks();
    Swal.fire("Deleted!", "Your task has been deleted.", "success");
  } catch (err) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "Failed to delete task",
    });
  }
};

// Toggle Completion
const toggleStatus = async (task) => {
  try {
    await axios.put(`${API_URL}/${task.id}`, {
      is_completed: !task.is_completed,
    });
    await fetchTasks();
  } catch (err) {
    console.error(err);
  }
};

// Edit Mode
const editTask = (task) => {
  isEditing.value = true;
  formData.value = {
    id: task.id,
    title: task.title,
    priority: task.priority,
    due_date: task.due_date || "",
  };
};

const resetForm = () => {
  isEditing.value = false;
  formData.value = {
    id: null,
    title: "",
    priority: 3,
    due_date: "",
  };
};

onMounted(() => {
  fetchTasks();
});

const filteredTasks = computed(() => {
  let result = [...tasks.value];

  // Filter
  if (filterStatus.value === "pending") {
    result = result.filter((t) => !t.is_completed);
  } else if (filterStatus.value === "completed") {
    result = result.filter((t) => t.is_completed);
  }

  // Sort
  result.sort((a, b) => {
    if (sortBy.value === "priority") {
      return a.priority - b.priority; // Ascending: 1 (High) -> 3 (Low)
    } else if (sortBy.value === "due_date") {
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return new Date(a.due_date) - new Date(b.due_date);
    }
    return 0;
  });

  return result;
});
</script>

<template>
  <div class="task-manager">
    <!-- Task Form -->
    <div class="task-form">
      <h3>{{ isEditing ? "Edit Task" : "Add New Task" }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <input
            v-model="formData.title"
            placeholder="Task Title"
            required
            class="input-field"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <select v-model="formData.priority" class="input-field">
              <option :value="1">High Priority</option>
              <option :value="2">Medium Priority</option>
              <option :value="3">Low Priority</option>
            </select>
          </div>

          <div class="form-group">
            <input
              type="date"
              v-model="formData.due_date"
              class="input-field"
            />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            {{ isEditing ? "Update Task" : "Add Task" }}
          </button>
          <button
            v-if="isEditing"
            type="button"
            @click="resetForm"
            class="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Task List -->
    <div class="task-list-container">
      <div class="list-header">
        <h3>Your Tasks</h3>
        <div class="controls">
          <select v-model="filterStatus" class="control-select">
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
          <select v-model="sortBy" class="control-select">
            <option value="priority">Sort by Priority</option>
            <option value="due_date">Sort by Due Date</option>
          </select>
        </div>
      </div>

      <!-- Skeleton Loading -->
      <div v-if="isLoading" class="skeleton-container">
        <div v-for="n in 3" :key="n" class="skeleton-task">
          <div class="skeleton-content">
            <div class="skeleton-line title"></div>
            <div class="skeleton-line badge"></div>
          </div>
          <div class="skeleton-actions">
            <div class="skeleton-circle"></div>
            <div class="skeleton-circle"></div>
          </div>
        </div>
      </div>

      <div v-else-if="tasks.length === 0" class="empty-state">
        No tasks found. Add one above!
      </div>

      <ul v-else class="task-list">
        <li
          v-for="task in filteredTasks"
          :key="task.id"
          :class="['task-item', { completed: task.is_completed }]"
        >
          <div class="task-content">
            <div class="task-header">
              <input
                type="checkbox"
                :checked="task.is_completed"
                @change="toggleStatus(task)"
                class="checkbox"
              />
              <span class="task-title">{{ task.title }}</span>
              <span :class="['badge', priorityClasses[task.priority]]">
                {{ priorityLabels[task.priority] }}
              </span>
            </div>

            <div class="task-meta">
              <span v-if="task.due_date" class="due-date">
                Due: {{ task.due_date }}
              </span>
            </div>
          </div>

          <div class="task-actions">
            <button @click="editTask(task)" class="btn-icon">
              <Icon icon="mdi:pencil" width="18" />
            </button>

            <button @click="deleteTask(task.id)" class="btn-icon delete">
              <Icon icon="mdi:trash-can" width="18" />
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.task-manager {
  max-width: 100%;
}

.task-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box; /* Important for width: 100% */
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-primary {
  background-color: #42b983;
  color: white;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
  margin-left: 10px;
}

.task-list {
  list-style: none;
  padding: 0;
}

.task-item {
  background: white;
  border: 1px solid #eee;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: #888;
}

.task-content {
  flex: 1;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.task-title {
  font-size: 1.1em;
  font-weight: 500;
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.badge {
  font-size: 0.8em;
  padding: 2px 8px;
  border-radius: 12px;
  color: white;
}

.priority-high {
  background-color: #e74c3c;
}
.priority-medium {
  background-color: #f39c12;
}
.priority-low {
  background-color: #3498db;
}

.task-meta {
  margin-left: 30px;
  font-size: 0.9em;
  color: #666;
}

.task-actions {
  display: flex;
  gap: 5px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2em;
  padding: 5px;
}

.btn-icon:hover {
  transform: scale(1.1);
}

.btn-icon.delete:hover {
  filter: hue-rotate(180deg); /* Simplistic red shift */
}

/* Skeleton Loading Styles */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-task {
  background: white;
  border: 1px solid #eee;
  padding: 15px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skeleton-content {
  flex: 1;
}

.skeleton-actions {
  display: flex;
  gap: 5px;
}

.skeleton-line {
  background: #eee;
  height: 20px;
  border-radius: 4px;
  margin-bottom: 5px;
  animation: pulse 1.5s infinite ease-in-out;
}

.skeleton-line.title {
  width: 60%;
  height: 24px;
}

.skeleton-line.badge {
  width: 20%;
  height: 16px;
  margin-top: 5px;
}

.skeleton-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #eee;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.controls {
  display: flex;
  gap: 10px;
}

.control-select {
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #ddd;
}
</style>

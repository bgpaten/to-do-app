<script setup>
import TaskList from './components/TaskList.vue'
</script>

<template>
  <div class="container">
    <header>
      <h1>Todo List</h1>
    </header>
    <main>
      <TaskList />
    </main>
  </div>
</template>

<style>
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f4f9;
  color: #333;
  margin: 0;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #eee;
  padding-bottom: 20px;
}

h1 {
  margin: 0;
  color: #2c3e50;
}
</style>

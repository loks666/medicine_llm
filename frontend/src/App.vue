<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 根组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f5f5f5;
}

#app {
  height: 100vh;
  width: 100vw;
}
</style>
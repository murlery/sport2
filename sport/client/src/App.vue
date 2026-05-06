<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;

  /* Фон */
  background-image: url("./assets/background.png");
  background-size: cover;        /* растянуть на весь экран */
  background-position: center;   /* по центру */
  background-repeat: no-repeat;  /* без повторения */
  background-attachment: fixed;  /* фиксированный фон */
}

#app {
  padding: 0px;
}
</style>
<template>
  <div class="container mt-4">
    <h2>Movies</h2>
    <div class="row">
      <div v-for="movie in movies" :key="movie.id" class="col-md-6 mb-3">
        <div class="card d-flex flex-row">
          <img :src="movie.poster" class="card-img-left" style="width:120px; object-fit:cover;" />
          <div class="card-body">
            <h5 class="card-title">{{ movie.title }}</h5>
            <p class="card-text">{{ movie.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const movies = ref([])

function fetchMovies() {
  fetch('/api/v1/movies')
    .then(r => r.json())
    .then(data => { movies.value = data.movies })
    .catch(console.error)
}

onMounted(() => {
  fetchMovies()
})
</script>
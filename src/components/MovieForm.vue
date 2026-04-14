<template>
  <form id="movieForm" @submit.prevent="saveMovie" enctype="multipart/form-data">
    <div class="form-group mb-3">
      <label for="title" class="form-label">Movie Title</label>
      <input type="text" id="title" name="title" v-model="title" class="form-control" />
    </div>

    <div class="form-group mb-3">
      <label for="description" class="form-label">Description</label>
      <textarea id="description" name="description" v-model="description" class="form-control" rows="4"></textarea>
    </div>

    <div class="form-group mb-3">
      <label for="poster" class="form-label">Movie Poster</label>
      <input type="file" id="poster" name="poster" @change="onFileChange" class="form-control" accept="image/*" />
    </div>

    <div v-if="errors.length" class="alert alert-danger">
      <ul class="mb-0">
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <button type="submit" class="btn btn-primary">Add Movie</button>
  </form>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const title = ref('')
const description = ref('')
const poster = ref(null)
const errors = ref([])
const successMessage = ref('')
const csrf_token = ref('')

onMounted(() => {
  getCsrfToken()
})

function getCsrfToken() {
  fetch('/api/v1/csrf-token')
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      csrf_token.value = data.csrf_token
    })
}

function onFileChange(event) {
  poster.value = event.target.files[0]
}

function saveMovie() {
  errors.value = []
  successMessage.value = ''

  let movieForm = document.getElementById('movieForm')
  let form_data = new FormData(movieForm)

  fetch('/api/v1/movies', {
    method: 'POST',
    body: form_data,
    headers: {
      'X-CSRFToken': csrf_token.value
    }
  })
    .then(function (response) {
      return response.json().then(function (data) {
        return { status: response.status, body: data }
      })
    })
    .then(function ({ status, body }) {
      console.log(status, body)
      if (body.errors) {
        errors.value = body.errors
      } else if (body.message) {
        successMessage.value = body.message
        title.value = ''
        description.value = ''
        poster.value = null
        movieForm.reset()
      }
    })
    .catch(function (error) {
      console.error(error)
      errors.value = ['An unexpected error occurred. Please try again.']
    })
}
</script>

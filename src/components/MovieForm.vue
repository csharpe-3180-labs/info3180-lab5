<template>
  <form @submit.prevent="saveMovie" enctype="multipart/form-data">
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
import { ref } from 'vue'

const title = ref('')
const description = ref('')
const poster = ref(null)
const errors = ref([])
const successMessage = ref('')

function onFileChange(event) {
  poster.value = event.target.files[0]
}

function saveMovie() {
  errors.value = []
  successMessage.value = ''

  const formData = new FormData()
  formData.append('title', title.value)
  formData.append('description', description.value)
  if (poster.value) {
    formData.append('poster', poster.value)
  }

  fetch('/api/v1/movies', {
    method: 'POST',
    body: formData
  })
    .then(function (response) {
      return response.json()
    })
    .then(function (data) {
      if (data.errors) {
        errors.value = data.errors
      } else {
        successMessage.value = data.message
        console.log(data)
      }
    })
    .catch(function (error) {
      console.log(error)
    })
}
</script>

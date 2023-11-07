document.getElementById('searchBar').addEventListener('keydown', async function (event) {
  if (event.key === 'Enter') {
    const searchBarContent = this.value;
    // Call the search API with the search bar content
    await searchModels(searchBarContent);
  }
});

async function searchModels(query) {
  try {
    const response = await fetch(`/api/search?query=${query}`);
    
    if (response.ok) {
      console.log('Success, start creating cards');
      const data = await response.json(); // parse the response into JSON
      await GenerateCards(data); // pass the parsed data to GenerateCards function
    } else {
      console.error('Error:', response.statusText);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}


async function GenerateCards(data) {
  if (data.status === 'success') {
    const container = document.getElementById('galleryContainer');
    // clear the existing cards
    container.innerHTML = '';

    const cards = data.data.slice(0, 10).map((result) => createCard(result.item));
    container.append(...cards);
  }
}


function createCard(item) {
  const card = document.createElement('div');
  card.className = 'col-xl-4 col-lg-6 col-md-12 mb-4';  // Adjust column classes as needed.

  const tagsHtml = item.tags.map(tag => `<p>${tag}</p>`).join('');

  const moreLink = document.createElement('a');
  moreLink.textContent = '... [more]';
  moreLink.href = '#';

  const lessLink = document.createElement('a');
  lessLink.textContent = ' [less]';
  lessLink.href = '#';

  const fullDescription = document.createElement('p');
  fullDescription.className = 'description full hidden'; // initially hidden
  fullDescription.textContent = item.description;
  fullDescription.appendChild(lessLink);

  const truncatedDescription = document.createElement('p');
  truncatedDescription.className = 'description truncated'; // initially visible
  truncatedDescription.textContent = item.description.slice(0, 100); // adjust the number as needed
  truncatedDescription.appendChild(moreLink);

  moreLink.addEventListener('click', function(event) {
    event.preventDefault(); // prevent the default link behavior
    truncatedDescription.classList.toggle('hidden');
    fullDescription.classList.toggle('hidden');
  });

  lessLink.addEventListener('click', function(event) {
    event.preventDefault(); // prevent the default link behavior
    truncatedDescription.classList.toggle('hidden');
    fullDescription.classList.toggle('hidden');
  });
  
  card.innerHTML = `
    <div class="gallery-item h-100">
      <div class="user-info d-flex align-items-center">
        <i class="bi bi-person user-icon"></i>
        <span class="user-name">${item.name}</span>
        <a href="#" class="btn btn-sm btn-outline-primary ms-auto more-button">
          <i class="bi bi-three-dots"></i>
        </a>
      </div>
      <div class="image-container position-relative">
        <img src="${item.pictureLink}" class="img-fluid" alt="">
        <div class="gallery-links d-flex align-items-center justify-content-center">
          <a href="${item.pictureLink}" title="${item.name}" class="glightbox preview-link">
            <i class="bi bi-arrows-angle-expand"></i>
          </a>
          <a href="${item.downloadLink}" class="details-link">
            <i class="bi bi-link-45deg"></i>
          </a>
        </div>
      </div>
      <div class="description-container">
    </div>
      <div class="tags">
        ${tagsHtml}
      </div>
      <div class="state-bar d-flex align-items-center">
      <div class="state-item likes">
        <i class="bi bi-heart state-icon"></i>
        <span class="state-count">${item.like}</span> Likes
      </div>
      <div class="state-item views">
        <i class="bi bi-eye state-icon"></i>
        <span class="state-count">${item.view}</span> Views
      </div>
      <div class="state-item shares">
        <i class="bi bi-share state-icon"></i>
        <span class="state-count">${item.share}</span> Shares
      </div>
  </div>
    </div>`;

    const descriptionContainer = card.querySelector(".description-container");
    descriptionContainer.appendChild(truncatedDescription);
    descriptionContainer.appendChild(fullDescription);
    
    
  return card;
}

  
  
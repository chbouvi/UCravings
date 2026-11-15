// Frontend behavior only. Food matching belongs to the backend.
const favoritesKey = 'foodfinder-favorites-v2';
const hallNames = {
  berkshire: 'Berkshire',
  worcester: 'Worcester',
  hampshire: 'Hampshire',
  franklin: 'Franklin',
};
const mealNames = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  grabngo: "Grab n' Go",
  latenight: 'Late Night',
};

const favoriteForm = document.querySelector('#favorite-form');
const favoriteInput = document.querySelector('#favorite-input');
const favoriteList = document.querySelector('#favorite-list');
const favoriteEmpty = document.querySelector('#favorite-empty');
const favoriteCount = document.querySelector('#favorite-count');
const searchForm = document.querySelector('#search-form');
const searchButton = document.querySelector('#search-button');
const searchMealSelect = document.querySelector('#search-meal');
const searchDate = document.querySelector('#search-date');
const searchStatus = document.querySelector('#search-status');
const results = document.querySelector('#results');
const resultList = document.querySelector('#result-list');
const hallSelect = document.querySelector('#hall-select');
const mealSelect = document.querySelector('#meal-select');
const menuStatus = document.querySelector('#menu-status');
const menuContent = document.querySelector('#menu-content');
const menuLabel = document.querySelector('#menu-label');
const menuList = document.querySelector('#menu-list');
const officialLink = document.querySelector('#official-link');

function loadFavorites() {
  try {
    const value = JSON.parse(localStorage.getItem(favoritesKey));
    return Array.isArray(value) ? value.filter(item => typeof item === 'string') : [];
  } catch {
    return [];
  }
}

let favorites = loadFavorites();
let menus = {};
let snapshotDate = null;

function saveFavorites() {
  localStorage.setItem(favoritesKey, JSON.stringify(favorites));
}

function renderFavorites() {
  favoriteList.replaceChildren();
  favoriteEmpty.hidden = favorites.length > 0;
  favoriteCount.textContent = String(favorites.length);
  favoriteCount.setAttribute('aria-label', `${favorites.length} favorites`);
  searchButton.disabled = favorites.length === 0;

  favorites.forEach((name, index) => {
    const item = document.createElement('li');
    const label = document.createElement('span');
    label.textContent = name;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'remove-favorite';
    remove.textContent = '×';
    remove.setAttribute('aria-label', `Remove ${name}`);
    remove.addEventListener('click', () => {
      favorites.splice(index, 1);
      saveFavorites();
      renderFavorites();
    });
    item.append(label, remove);
    favoriteList.append(item);
  });
}

favoriteForm.addEventListener('submit', event => {
  event.preventDefault();
  const name = favoriteInput.value.trim();
  if (!name) return;
  if (!favorites.some(saved => saved.toLocaleLowerCase() === name.toLocaleLowerCase())) {
    favorites.push(name);
    saveFavorites();
    renderFavorites();
  }
  favoriteInput.value = '';
  favoriteInput.focus();
});

function makeOption(value, text) {
  const option = document.createElement('option');
  option.value = value;
  option.textContent = text;
  return option;
}

function updateSearchMeals() {
  const available = new Set(Object.values(menus).flatMap(meals => Object.keys(meals)));
  const previous = searchMealSelect.value;
  const options = [makeOption('All meals', 'All meals')];
  for (const meal of Object.keys(mealNames)) {
    if (available.has(meal)) options.push(makeOption(mealNames[meal], mealNames[meal]));
  }
  searchMealSelect.replaceChildren(...options);
  if ([...searchMealSelect.options].some(option => option.value === previous)) searchMealSelect.value = previous;
}

function updateMealOptions() {
  const available = menus[hallSelect.value] || {};
  const previous = mealSelect.value;
  mealSelect.replaceChildren(...Object.keys(available).map(meal => makeOption(meal, mealNames[meal] || meal)));
  if (available[previous]) mealSelect.value = previous;
  mealSelect.disabled = mealSelect.options.length === 0;
  renderMenu();
}

function renderMenu() {
  const hall = hallSelect.value;
  const meal = mealSelect.value;
  const dishes = menus[hall]?.[meal];
  menuList.replaceChildren();
  if (!Array.isArray(dishes)) {
    menuContent.hidden = true;
    menuStatus.textContent = 'No saved menu for this selection.';
    return;
  }
  dishes.forEach(name => {
    const item = document.createElement('li');
    item.textContent = name;
    menuList.append(item);
  });
  menuLabel.textContent = `${hallNames[hall] || hall} · ${mealNames[meal] || meal} · ${dishes.length} items`;
  officialLink.href = `https://www.umassdining.com/locations-menus/${hall}/menu`;
  menuStatus.textContent = snapshotDate ? `Snapshot saved on ${snapshotDate}.` : 'Snapshot date not provided.';
  menuContent.hidden = false;
}

hallSelect.addEventListener('change', updateMealOptions);
mealSelect.addEventListener('change', renderMenu);

async function loadMenus() {
  try {
    const response = await fetch('./menus.json');
    if (!response.ok) throw new Error('Could not load menus.json.');
    const data = await response.json();
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Menu data has an unexpected format.');
    menus = data.halls || data;
    snapshotDate = typeof data.date === 'string' ? data.date : null;
    if (!menus || typeof menus !== 'object' || Array.isArray(menus)) throw new Error('Menu data has no dining halls.');
    if (snapshotDate) {
      const date = new Date(`${snapshotDate}T12:00:00`);
      searchDate.textContent = Number.isNaN(date.getTime())
        ? `Saved ${snapshotDate}`
        : `Saved ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
    hallSelect.replaceChildren(...Object.keys(menus).map(hall => makeOption(hall, hallNames[hall] || hall)));
    hallSelect.disabled = hallSelect.options.length === 0;
    updateSearchMeals();
    updateMealOptions();
  } catch (error) {
    menuStatus.textContent = `${error.message} Run this page through a local web server.`;
    menuStatus.classList.add('error');
  }
}

function renderResults(matches) {
  resultList.replaceChildren();
  results.hidden = false;
  if (!matches.length) {
    const empty = document.createElement('p');
    empty.className = 'muted';
    empty.textContent = 'No matches were returned.';
    resultList.append(empty);
    return;
  }

  // One dish can appear at several halls and meals; show it once with its locations.
  const grouped = new Map();
  matches.forEach(match => {
    const key = JSON.stringify([match.name, match.match_type, match.matched_favorite]);
    if (!grouped.has(key)) grouped.set(key, { match, halls: new Map() });
    const group = grouped.get(key);
    const hall = String(match.hall || 'Unknown hall');
    if (!group.halls.has(hall)) group.halls.set(hall, { details: new Set(), sourceUrl: null });
    const location = group.halls.get(hall);
    const meal = String(match.meal || 'Meal not listed');
    const mealLabel = mealNames[meal.toLowerCase()] || meal;
    location.details.add([mealLabel, match.station].filter(Boolean).join(' · '));
    if (match.source_url && !location.sourceUrl) {
      try {
        const url = new URL(match.source_url);
        if (url.protocol === 'https:' || url.protocol === 'http:') location.sourceUrl = url.href;
      } catch { /* Ignore invalid URLs from a backend response. */ }
    }
  });

  const exactCards = document.createElement('div');
  const similarCards = document.createElement('div');
  grouped.forEach(({ match, halls }) => {
    const card = document.createElement('article');
    card.className = 'result-card';
    const heading = document.createElement('h4');
    heading.textContent = match.name || 'Unnamed item';
    card.append(heading);
    const isSimilar = String(match.match_type).toLowerCase() === 'similar';
    if (isSimilar && match.matched_favorite) {
      const favorite = document.createElement('p');
      favorite.textContent = `Similar to ${match.matched_favorite}`;
      card.append(favorite);
    }
    const locations = document.createElement('ul');
    locations.className = 'result-locations';
    halls.forEach(({ details, sourceUrl }, hall) => {
      const item = document.createElement('li');
      const hallLabel = document.createElement('strong');
      hallLabel.textContent = hallNames[hall.toLowerCase()] || hall;
      const meals = document.createElement('span');
      meals.textContent = [...details].join(', ');
      item.append(hallLabel, meals);
      if (sourceUrl) {
        const link = document.createElement('a');
        link.href = sourceUrl;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Official menu ↗';
        item.append(link);
      }
      locations.append(item);
    });
    card.append(locations);
    (isSimilar ? similarCards : exactCards).append(card);
  });

  for (const [title, cards] of [['Your favorites', exactCards], ['Similar suggestions', similarCards]]) {
    if (!cards.childElementCount) continue;
    const section = document.createElement('section');
    section.className = 'result-section';
    const heading = document.createElement('h3');
    heading.textContent = `${title} (${cards.childElementCount})`;
    section.append(heading, cards);
    resultList.append(section);
  }
}

searchForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (!favorites.length) return;
  results.hidden = true;
  searchStatus.classList.remove('error');
  searchStatus.textContent = 'Searching…';
  searchButton.disabled = true;
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ favorites, meal: searchMealSelect.value }),
    });
    if (response.status === 404 || response.status === 501) {
      throw new Error('Search is not connected yet. You can browse the saved menus below.');
    }
    if (!response.ok) throw new Error(`Search failed (${response.status}).`);
    const data = await response.json();
    if (!Array.isArray(data.matches)) throw new Error('Search returned an unexpected response.');
    renderResults(data.matches);
    searchStatus.textContent = '';
  } catch (error) {
    searchStatus.textContent = error.message;
    searchStatus.classList.add('error');
  } finally {
    searchButton.disabled = favorites.length === 0;
  }
});

renderFavorites();
loadMenus();

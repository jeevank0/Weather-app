function capitalizeWord(word) {
  if (!word) return '';
  return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}

export function formatLocationName(value) {
  if (typeof value !== 'string') return '';

  return value
    .split(',')
    .map((segment) => segment.trim())
    .filter(Boolean)
    .map((segment) => segment.split(/\s+/).map(capitalizeWord).join(' '))
    .join(', ');
}

import { useState } from 'react';

function SearchBar({ onSearch, isLoading }) {
  const [location, setLocation] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    onSearch(location);
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <input
        type="text"
        value={location}
        onChange={(event) => setLocation(event.target.value)}
        placeholder="Enter location (e.g. Chennai)"
        aria-label="Location"
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Loading weather...' : 'Get Weather'}
      </button>
    </form>
  );
}

export default SearchBar;

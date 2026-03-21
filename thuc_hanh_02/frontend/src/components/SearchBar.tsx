import React from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  query: string;
  placeholder?: string;
  onChange: (value: string) => void;
  onSearch: (e?: React.FormEvent) => void;
  onClear: () => void;
  variant?: 'large' | 'small';
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  placeholder = "Tìm kiếm tài liệu...",
  onChange,
  onSearch,
  onClear,
  variant = 'large'
}) => {
  const isLarge = variant === 'large';

  return (
    <form onSubmit={onSearch} className="w-full">
      <div className={`relative flex items-center w-full border border-[#dfe1e5] rounded-full px-5 hover:shadow-md focus-within:shadow-md transition-shadow group-focus-within:border-transparent ${isLarge ? 'py-3' : 'py-2'}`}>
        {isLarge && <Search size={20} className="text-gray-400 mr-3" />}
        <input
          type="text"
          value={query}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`flex-grow outline-none ${isLarge ? 'text-lg' : 'text-base'}`}
          autoFocus={isLarge}
        />
        <div className="flex items-center gap-3 ml-2">
          {query && (
            <button type="button" onClick={onClear} className="p-1 hover:text-gray-700 text-gray-400">
              <X size={20} />
            </button>
          )}
          {!isLarge && (
            <Search size={20} className="text-[#4285F4] cursor-pointer" onClick={() => onSearch()} />
          )}
        </div>
      </div>
    </form>
  );
};

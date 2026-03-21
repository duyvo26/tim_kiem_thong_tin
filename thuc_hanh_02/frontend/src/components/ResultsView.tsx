import React from 'react';
import { Search } from 'lucide-react';
import { Logo } from './Logo';
import { SearchBar } from './SearchBar';
import { ResultItem } from './ResultItem';
import { Pagination } from './Pagination';
import { ResultsFooter } from './ResultsFooter';
import { SearchResult } from '../types';

interface ResultsViewProps {
  query: string;
  setQuery: (val: string) => void;
  handleSearch: (e?: React.FormEvent) => void;
  resetSearch: () => void;
  loading: boolean;
  searchTime: number;
  totalResults: number;
  results: SearchResult[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  hasSearched: boolean;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  query,
  setQuery,
  handleSearch,
  resetSearch,
  loading,
  searchTime,
  totalResults,
  results,
  currentPage,
  totalPages,
  onPageChange,
  hasSearched
}) => {
  return (
    <div className="min-h-screen bg-white text-[#202124] font-sans flex flex-col">
      <header className="sticky top-0 bg-white z-10 border-b border-gray-200 pt-6 pb-2 px-4 md:px-8">
        <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8 max-w-[1200px]">
          <div onClick={resetSearch}>
            <Logo size="sm" className="cursor-pointer" />
          </div>

          <div className="w-full max-w-[692px]">
            <SearchBar 
              query={query} 
              onChange={setQuery} 
              onSearch={handleSearch} 
              onClear={() => setQuery('')}
              variant="small"
            />
          </div>
        </div>

        <div className="flex gap-6 mt-4 max-w-[1200px] md:ml-[160px] text-sm text-gray-600">
          <div className="flex items-center gap-1 border-b-2 border-[#1a73e8] pb-2 text-[#1a73e8] cursor-default">
            <Search size={16} /> All
          </div>
        </div>
      </header>

      <main className="flex-grow px-4 md:px-8 pt-4 pb-12 max-w-[1200px] md:ml-[160px]">
        <div className="text-sm text-gray-600 mb-6">
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-[#4285F4] border-t-transparent rounded-full animate-spin"></div>
              Searching...
            </div>
          ) : (
            `About ${totalResults} results (${searchTime.toFixed(2)} seconds)`
          )}
        </div>

        <div className="space-y-8 min-h-[400px]">
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="animate-pulse space-y-2 max-w-[652px]">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              </div>
            ))
          ) : results.length > 0 ? (
            results.map((result, index) => (
              <ResultItem key={index} result={result} index={index} />
            ))
          ) : !loading && hasSearched && (
            <div className="py-12">
              <p className="text-lg">Your search - <b>{query}</b> - did not match any documents.</p>
            </div>
          )}
        </div>

        {!loading && (
          <Pagination 
            currentPage={currentPage} 
            totalPages={totalPages} 
            onPageChange={onPageChange} 
          />
        )}
      </main>

      <ResultsFooter />
    </div>
  );
};

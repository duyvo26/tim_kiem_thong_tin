import React, { useState, useMemo } from 'react';
import { HomeView } from './components/HomeView';
import { ResultsView } from './components/ResultsView';
import { SearchResult } from './types';

const RESULTS_PER_PAGE = 10;

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  // Mock data generator
  const generateMockResults = (searchTerm: string): SearchResult[] => {
    return Array.from({ length: 50 }).map((_, i) => ({
      title: `${searchTerm} - Tài liệu hướng dẫn chi tiết phần ${i + 1}`,
      url: `https://example.com/docs/${searchTerm.toLowerCase().replace(/\s+/g, '-')}/p${i + 1}`,
      snippet: `Đây là kết quả tìm kiếm giả lập cho truy vấn "${searchTerm}". Tài liệu này cung cấp thông tin chi tiết về phần ${i + 1} của chủ đề bạn đang quan tâm. Nội dung bao gồm các bước hướng dẫn, ví dụ minh họa và các lưu ý quan trọng.`
    }));
  };

  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);
    setCurrentPage(1);
    const startTime = performance.now();

    // Simulate network delay
    setTimeout(() => {
      const mockData = generateMockResults(query);
      setResults(mockData);
      setSearchTime((performance.now() - startTime) / 1000);
      setLoading(false);
    }, 600);
  };

  const resetSearch = () => {
    setHasSearched(false);
    setQuery('');
    setResults([]);
    setCurrentPage(1);
  };

  const paginatedResults = useMemo(() => {
    const startIndex = (currentPage - 1) * RESULTS_PER_PAGE;
    return results.slice(startIndex, startIndex + RESULTS_PER_PAGE);
  }, [results, currentPage]);

  const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);

  if (!hasSearched) {
    return (
      <HomeView 
        query={query} 
        setQuery={setQuery} 
        handleSearch={handleSearch} 
      />
    );
  }

  return (
    <ResultsView
      query={query}
      setQuery={setQuery}
      handleSearch={handleSearch}
      resetSearch={resetSearch}
      loading={loading}
      searchTime={searchTime}
      totalResults={results.length}
      results={paginatedResults}
      currentPage={currentPage}
      totalPages={totalPages}
      onPageChange={setCurrentPage}
      hasSearched={hasSearched}
    />
  );
}

import React, { useState, useMemo } from 'react';
import { Search, X, Mic, Camera, MoreVertical, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion } from 'motion/react';

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
}

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
      <div className="min-h-screen flex flex-col bg-white text-[#202124] font-sans">
        {/* Header - Empty */}
        <header className="h-16" />

        {/* Main Content */}
        <main className="flex-grow flex flex-col items-center pt-[15vh]">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center w-full max-w-[584px] px-4"
          >
            {/* Logo */}
            <div className="mb-8 select-none cursor-default">
              <span className="text-7xl font-bold tracking-tighter flex">
                <span className="text-[#4285F4]">G</span>
                <span className="text-[#EA4335]">o</span>
                <span className="text-[#FBBC05]">o</span>
                <span className="text-[#4285F4]">S</span>
                <span className="text-[#34A853]">e</span>
                <span className="text-[#EA4335]">a</span>
                <span className="text-[#FBBC05]">r</span>
                <span className="text-[#4285F4]">c</span>
                <span className="text-[#34A853]">h</span>
              </span>
            </div>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="w-full group">
              <div className="relative flex items-center w-full border border-[#dfe1e5] rounded-full px-5 py-3 hover:shadow-md focus-within:shadow-md transition-shadow group-focus-within:border-transparent">
                <Search size={20} className="text-gray-400 mr-3" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-grow outline-none text-lg"
                  autoFocus
                />
                <div className="flex items-center gap-3 ml-2">
                  {query && (
                    <button type="button" onClick={() => setQuery('')} className="p-1 hover:text-gray-700 text-gray-400">
                      <X size={20} />
                    </button>
                  )}
                </div>
              </div>
            </form>
          </motion.div>
        </main>

        {/* Footer */}
        <footer className="bg-[#f2f2f2] text-sm text-[#70757a]">
          <div className="px-8 py-3 border-b border-[#dadce0]">Vietnam</div>
          <div className="px-8 py-3 flex flex-wrap justify-between">
            <div className="flex gap-6">
              <a href="#" className="hover:underline">About</a>
              <a href="#" className="hover:underline">Advertising</a>
              <a href="#" className="hover:underline">Business</a>
              <a href="#" className="hover:underline">How Search works</a>
            </div>
            <div className="flex gap-6">
              <a href="#" className="hover:underline">Privacy</a>
              <a href="#" className="hover:underline">Terms</a>
              <a href="#" className="hover:underline">Settings</a>
            </div>
          </div>
        </footer>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white text-[#202124] font-sans flex flex-col">
      {/* Results Header */}
      <header className="sticky top-0 bg-white z-10 border-b border-gray-200 pt-6 pb-2 px-4 md:px-8">
        <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8 max-w-[1200px]">
          <div className="cursor-pointer select-none" onClick={resetSearch}>
            <span className="text-3xl font-bold tracking-tighter flex">
              <span className="text-[#4285F4]">G</span>
              <span className="text-[#EA4335]">o</span>
              <span className="text-[#FBBC05]">o</span>
              <span className="text-[#4285F4]">S</span>
              <span className="text-[#34A853]">e</span>
              <span className="text-[#EA4335]">a</span>
              <span className="text-[#FBBC05]">r</span>
              <span className="text-[#4285F4]">c</span>
              <span className="text-[#34A853]">h</span>
            </span>
          </div>

          <form onSubmit={handleSearch} className="w-full max-w-[692px]">
            <div className="flex items-center w-full border border-[#dfe1e5] rounded-full px-5 py-2 hover:shadow-md focus-within:shadow-md transition-shadow">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-grow outline-none text-base"
              />
              <div className="flex items-center gap-3 ml-2">
                {query && (
                  <button type="button" onClick={() => setQuery('')} className="p-1 hover:text-gray-700 text-gray-400">
                    <X size={20} />
                  </button>
                )}
                <Search size={20} className="text-[#4285F4] cursor-pointer" onClick={() => handleSearch()} />
              </div>
            </div>
          </form>
        </div>

        {/* Single Tab */}
        <div className="flex gap-6 mt-4 max-w-[1200px] md:ml-[160px] text-sm text-gray-600">
          <div className="flex items-center gap-1 border-b-2 border-[#1a73e8] pb-2 text-[#1a73e8] cursor-default">
            <Search size={16} /> All
          </div>
        </div>
      </header>

      {/* Results Content */}
      <main className="flex-grow px-4 md:px-8 pt-4 pb-12 max-w-[1200px] md:ml-[160px]">
        <div className="text-sm text-gray-600 mb-6">
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-[#4285F4] border-t-transparent rounded-full animate-spin"></div>
              Searching...
            </div>
          ) : (
            `About ${results.length} results (${searchTime.toFixed(2)} seconds)`
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
          ) : paginatedResults.length > 0 ? (
            paginatedResults.map((result, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-[652px] group"
              >
                <div className="flex flex-col">
                  <div className="flex items-center gap-2 text-sm mb-1">
                    <div className="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
                      <Search size={14} className="text-gray-400" />
                    </div>
                    <div className="flex flex-col overflow-hidden">
                      <span className="text-[#202124] text-sm truncate">{new URL(result.url).hostname}</span>
                      <span className="text-[#70757a] text-xs truncate">{result.url}</span>
                    </div>
                    <button className="ml-auto p-1 text-gray-400 hover:text-gray-600">
                      <MoreVertical size={16} />
                    </button>
                  </div>
                  <a href={result.url} target="_blank" rel="noopener noreferrer" className="group">
                    <h3 className="text-[#1a0dab] text-xl font-medium hover:underline mb-1">
                      {result.title}
                    </h3>
                  </a>
                  <p className="text-[#4d5156] text-sm leading-relaxed">
                    {result.snippet}
                  </p>
                </div>
              </motion.div>
            ))
          ) : !loading && hasSearched && (
            <div className="py-12">
              <p className="text-lg">Your search - <b>{query}</b> - did not match any documents.</p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {!loading && results.length > 0 && (
          <div className="mt-12 flex items-center gap-4 text-sm text-[#1a73e8]">
            <button 
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className={`flex items-center gap-1 hover:underline ${currentPage === 1 ? 'invisible' : ''}`}
            >
              <ChevronLeft size={16} /> Previous
            </button>
            
            <div className="flex items-center gap-2">
              {Array.from({ length: Math.min(10, totalPages) }).map((_, i) => {
                const pageNum = i + 1;
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                      currentPage === pageNum ? 'text-black font-bold cursor-default' : 'hover:bg-gray-100'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>

            <button 
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className={`flex items-center gap-1 hover:underline ${currentPage === totalPages ? 'invisible' : ''}`}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        )}
      </main>

      {/* Results Footer */}
      <footer className="bg-[#f2f2f2] text-sm text-[#70757a] mt-auto">
        <div className="px-4 md:px-8 py-3 border-b border-[#dadce0] md:pl-[160px]">Vietnam</div>
        <div className="px-4 md:px-8 py-3 flex flex-wrap gap-6 md:pl-[160px]">
          <a href="#" className="hover:underline">Help</a>
          <a href="#" className="hover:underline">Send feedback</a>
          <a href="#" className="hover:underline">Privacy</a>
          <a href="#" className="hover:underline">Terms</a>
        </div>
      </footer>
    </div>
  );
}

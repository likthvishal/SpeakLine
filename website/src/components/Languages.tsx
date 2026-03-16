const languages = [
  { name: 'Python', ext: '.py', prefix: '#', icon: '🐍', color: 'from-yellow-400 to-blue-500' },
  { name: 'JavaScript', ext: '.js', prefix: '//', icon: '⚡', color: 'from-yellow-400 to-yellow-600' },
  { name: 'TypeScript', ext: '.ts', prefix: '//', icon: '💙', color: 'from-blue-400 to-blue-600' },
  { name: 'Go', ext: '.go', prefix: '//', icon: '🐹', color: 'from-cyan-400 to-cyan-600' },
  { name: 'Rust', ext: '.rs', prefix: '//', icon: '🦀', color: 'from-orange-400 to-red-600' },
  { name: 'Java', ext: '.java', prefix: '//', icon: '☕', color: 'from-red-400 to-orange-600' },
  { name: 'C#', ext: '.cs', prefix: '//', icon: '💜', color: 'from-purple-400 to-purple-600' },
  { name: 'Ruby', ext: '.rb', prefix: '#', icon: '💎', color: 'from-red-400 to-red-600' },
  { name: 'C/C++', ext: '.cpp', prefix: '//', icon: '⚙️', color: 'from-blue-400 to-indigo-600' },
];

export default function Languages() {
  return (
    <section id="languages" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Works With Your
            <span className="gradient-text"> Favorite Languages</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Auto-detect language from file extension. Perfect indentation and comment style every time.
          </p>
        </div>

        {/* Languages Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 max-w-4xl mx-auto">
          {languages.map((lang, index) => (
            <div
              key={index}
              className="group relative"
            >
              <div className="feature-card text-center py-6">
                <div className="text-4xl mb-3">{lang.icon}</div>
                <h3 className="text-white font-medium mb-1">{lang.name}</h3>
                <p className="text-slate-500 text-sm font-mono">{lang.ext}</p>

                {/* Hover Detail */}
                <div className="absolute inset-0 rounded-xl bg-slate-900/95 backdrop-blur flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <p className="text-slate-400 text-sm mb-2">Comment prefix:</p>
                  <code className="text-xl font-mono text-emerald-400">{lang.prefix}</code>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-12 text-center">
          <p className="text-slate-500 text-sm">
            Don't see your language?{' '}
            <a href="#" className="text-sky-400 hover:text-sky-300 underline">
              Use GenericParser
            </a>
            {' '}with any comment prefix.
          </p>
        </div>
      </div>
    </section>
  );
}

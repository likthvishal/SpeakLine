import { Github, Heart } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const links = {
    product: [
      { label: 'Features', href: '#features' },
      { label: 'Demo', href: '#demo' },
      { label: 'Installation', href: '#installation' },
      { label: 'API Reference', href: '#api' },
    ],
    resources: [
      { label: 'Documentation', href: 'https://github.com/likthvishal/SpeakLine#readme' },
      { label: 'GitHub', href: 'https://github.com/likthvishal/SpeakLine' },
      { label: 'PyPI', href: 'https://pypi.org/project/speakline' },
      { label: 'Changelog', href: 'https://github.com/likthvishal/SpeakLine/releases' },
    ],
    community: [
      { label: 'Contributing', href: 'https://github.com/likthvishal/SpeakLine/blob/master/README.md#contributing' },
      { label: 'Issues', href: 'https://github.com/likthvishal/SpeakLine/issues' },
      { label: 'Discussions', href: 'https://github.com/likthvishal/SpeakLine/discussions' },
    ],
  };

  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <a href="#" className="flex items-center gap-2 mb-4">
              <img src="/logo.png" alt="SpeakLine" className="h-9 w-9" />
              <span className="text-xl font-bold text-gray-900">SpeakLine</span>
            </a>
            <p className="text-gray-400 text-sm mb-4">
              Turn your spoken thoughts into well-formatted code comments.
            </p>
            <div className="flex gap-3">
              <a
                href="https://github.com/likthvishal/SpeakLine"
                className="p-2 rounded-lg bg-gray-100 text-gray-500 hover:text-gray-900 hover:bg-gray-200 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="text-gray-900 font-semibold mb-4 capitalize">{category}</h4>
              <ul className="space-y-2">
                {items.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-gray-900 transition-colors text-sm"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-gray-400 text-sm">
            &copy; {currentYear} SpeakLine. MIT License.
          </p>
          <p className="text-gray-400 text-sm flex items-center gap-1">
            Built with <Heart className="w-4 h-4 text-red-500" /> by developers who believe code comments should be as natural as talking.
          </p>
        </div>
      </div>
    </footer>
  );
}

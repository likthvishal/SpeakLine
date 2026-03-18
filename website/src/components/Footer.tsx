import { Mic, Github, Twitter, Heart } from 'lucide-react';

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
      { label: 'Twitter', href: 'https://twitter.com/speaklinedev' },
    ],
  };

  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <a href="#" className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-gradient-to-br from-sky-500 to-violet-500">
                <Mic className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">SpeakLine</span>
            </a>
            <p className="text-slate-500 text-sm mb-4">
              Turn your spoken thoughts into well-formatted code comments.
            </p>
            <div className="flex gap-3">
              <a
                href="https://github.com/likthvishal/SpeakLine"
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="text-white font-semibold mb-4 capitalize">{category}</h4>
              <ul className="space-y-2">
                {items.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-slate-500 hover:text-white transition-colors text-sm"
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
        <div className="mt-12 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-slate-500 text-sm">
            &copy; {currentYear} SpeakLine. MIT License.
          </p>
          <p className="text-slate-500 text-sm flex items-center gap-1">
            Built with <Heart className="w-4 h-4 text-red-500" /> by developers who believe code comments should be as natural as talking.
          </p>
        </div>
      </div>
    </footer>
  );
}

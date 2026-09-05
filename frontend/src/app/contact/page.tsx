import Link from 'next/link';
import { Radar, Mail, MessageSquare, Briefcase } from 'lucide-react';

export const metadata = {
  title: 'Contact — AI Intent Radar',
  description: 'Get in touch with the AI Intent Radar team.',
};

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-radar-950 via-radar-900 to-radar-950 text-white">

      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-radar-800 max-w-5xl mx-auto">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-radar-500 rounded-lg flex items-center justify-center">
            <Radar className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-bold">Intent Radar</span>
        </Link>
        <div className="flex items-center gap-6 text-sm text-radar-300">
          <Link href="/about" className="hover:text-white transition-colors">About</Link>
          <Link href="/contact" className="text-white font-medium">Contact</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
          <Link href="/auth/login" className="bg-radar-600 hover:bg-radar-500 text-white px-4 py-1.5 rounded-lg transition-colors">
            Sign in
          </Link>
        </div>
      </nav>

      {/* Header */}
      <section className="max-w-3xl mx-auto px-6 pt-20 pb-12 text-center">
        <h1 className="text-4xl font-bold mb-4">Get in touch</h1>
        <p className="text-radar-300 text-lg">
          Questions, feedback, partnership enquiries, or investor conversations — we want to hear from you.
        </p>
      </section>

      {/* Contact options */}
      <section className="max-w-3xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {[
            {
              icon: Mail,
              title: 'General Enquiries',
              desc: 'Questions about the product, pricing, or getting started.',
              contact: 'hello@intentradar.ai',
              href: 'mailto:hello@intentradar.ai',
            },
            {
              icon: Briefcase,
              title: 'Investors',
              desc: 'Funding conversations, due diligence, or partnership discussions.',
              contact: 'invest@intentradar.ai',
              href: 'mailto:invest@intentradar.ai',
            },
            {
              icon: MessageSquare,
              title: 'Support',
              desc: 'Help with your account, billing, or technical issues.',
              contact: 'support@intentradar.ai',
              href: 'mailto:support@intentradar.ai',
            },
          ].map(({ icon: Icon, title, desc, contact, href }) => (
            <a
              key={title}
              href={href}
              className="bg-radar-900/50 border border-radar-800 hover:border-radar-600 rounded-2xl p-6 transition-colors group"
            >
              <div className="w-10 h-10 bg-radar-700/50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-radar-600/50 transition-colors">
                <Icon className="w-5 h-5 text-radar-400" />
              </div>
              <h3 className="text-base font-semibold mb-2">{title}</h3>
              <p className="text-sm text-radar-300 mb-4 leading-relaxed">{desc}</p>
              <p className="text-sm text-radar-400 group-hover:text-radar-200 transition-colors font-medium">
                {contact} →
              </p>
            </a>
          ))}
        </div>

        {/* Contact form */}
        <div className="bg-radar-900/50 border border-radar-800 rounded-2xl p-8">
          <h2 className="text-xl font-semibold mb-6">Send us a message</h2>
          <form
            action="https://formspree.io/f/hello@intentradar.ai"
            method="POST"
            className="space-y-4"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-radar-300 mb-1">Name</label>
                <input
                  type="text"
                  name="name"
                  required
                  placeholder="Your name"
                  className="w-full px-4 py-2.5 bg-radar-800/50 border border-radar-700 rounded-lg text-sm text-white placeholder-radar-500 focus:outline-none focus:border-radar-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-radar-300 mb-1">Email</label>
                <input
                  type="email"
                  name="email"
                  required
                  placeholder="you@company.com"
                  className="w-full px-4 py-2.5 bg-radar-800/50 border border-radar-700 rounded-lg text-sm text-white placeholder-radar-500 focus:outline-none focus:border-radar-500 transition-colors"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-radar-300 mb-1">Subject</label>
              <select
                name="subject"
                className="w-full px-4 py-2.5 bg-radar-800/50 border border-radar-700 rounded-lg text-sm text-white focus:outline-none focus:border-radar-500 transition-colors"
              >
                <option value="general">General enquiry</option>
                <option value="investor">Investor / funding</option>
                <option value="partnership">Partnership</option>
                <option value="support">Support</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-radar-300 mb-1">Message</label>
              <textarea
                name="message"
                required
                rows={5}
                placeholder="Tell us what's on your mind..."
                className="w-full px-4 py-2.5 bg-radar-800/50 border border-radar-700 rounded-lg text-sm text-white placeholder-radar-500 focus:outline-none focus:border-radar-500 transition-colors resize-none"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-radar-600 hover:bg-radar-500 text-white font-medium py-2.5 rounded-lg text-sm transition-colors"
            >
              Send message
            </button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-radar-800 py-6 px-6 text-center text-xs text-radar-400">
        <div className="flex items-center justify-center gap-6 mb-2">
          <Link href="/about" className="hover:text-white transition-colors">About</Link>
          <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
        </div>
        <p>© {new Date().getFullYear()} AI Intent Radar. All rights reserved.</p>
      </footer>
    </div>
  );
}

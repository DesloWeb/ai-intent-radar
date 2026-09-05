import Link from 'next/link';
import { Radar } from 'lucide-react';

export const metadata = {
  title: 'Privacy Policy — AI Intent Radar',
  description: 'AI Intent Radar privacy policy — how we collect, use, and protect your data.',
};

const LAST_UPDATED = 'September 4, 2026';
const CONTACT_EMAIL = 'privacy@intentradar.ai';
const COMPANY_NAME = 'AI Intent Radar';

export default function PrivacyPage() {
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
          <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
          <Link href="/privacy" className="text-white font-medium">Privacy</Link>
          <Link href="/auth/login" className="bg-radar-600 hover:bg-radar-500 text-white px-4 py-1.5 rounded-lg transition-colors">
            Sign in
          </Link>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-6 pt-16 pb-20">
        <h1 className="text-3xl font-bold mb-2">Privacy Policy</h1>
        <p className="text-radar-400 text-sm mb-10">Last updated: {LAST_UPDATED}</p>

        <div className="space-y-10 text-sm text-radar-200 leading-relaxed">

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">1. Overview</h2>
            <p>
              {COMPANY_NAME} (&quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) operates the AI Intent Radar
              platform at intentradar.ai. This Privacy Policy explains how we collect, use,
              store, and protect your personal information when you use our service.
            </p>
            <p className="mt-3">
              By using our platform, you agree to the collection and use of information in
              accordance with this policy. If you do not agree, please do not use the service.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">2. Information We Collect</h2>
            <h3 className="font-medium text-white mb-2">Information you provide directly</h3>
            <ul className="list-disc list-inside space-y-1 mb-4">
              <li>Full name and email address (at registration)</li>
              <li>Password (stored as a bcrypt hash — we never store plaintext passwords)</li>
              <li>Organisation name (optional)</li>
              <li>Provider profiles you create (business name, services, locations)</li>
              <li>Feedback you submit on opportunities (saved, contacted, won, lost)</li>
              <li>Messages sent via our contact form</li>
            </ul>
            <h3 className="font-medium text-white mb-2">Information collected automatically</h3>
            <ul className="list-disc list-inside space-y-1 mb-4">
              <li>IP address and approximate location (used for rate limiting and security)</li>
              <li>Browser type and device information</li>
              <li>Pages viewed and features used within the platform</li>
              <li>API request logs (retained for 30 days for security monitoring)</li>
            </ul>
            <h3 className="font-medium text-white mb-2">Information we do not collect</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>Payment card details (we do not currently process payments directly)</li>
              <li>Social media profiles</li>
              <li>Biometric data</li>
              <li>Information from third parties about you</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">3. How We Use Your Information</h2>
            <p className="mb-3">We use the information we collect to:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Create and manage your account</li>
              <li>Provide the commercial intelligence service</li>
              <li>Match opportunities to your provider profile</li>
              <li>Improve our AI scoring and matching algorithms using anonymised feedback</li>
              <li>Send transactional emails (account confirmation, password reset)</li>
              <li>Respond to support and contact form submissions</li>
              <li>Detect and prevent fraud, abuse, and security threats</li>
              <li>Comply with legal obligations</li>
            </ul>
            <p className="mt-3">
              We do <strong className="text-white">not</strong> sell your personal data to third parties.
              We do <strong className="text-white">not</strong> use your data for advertising profiling.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">4. Data Storage and Security</h2>
            <p className="mb-3">
              Your data is stored on servers located in the United States. We use the following
              security measures to protect your information:
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li>All data transmitted over HTTPS/TLS encryption</li>
              <li>Passwords hashed using bcrypt (industry standard)</li>
              <li>JWT tokens with short expiry windows (60 minutes access, 7 days refresh)</li>
              <li>Redis-backed token revocation on logout</li>
              <li>Role-based access control — users only access their organisation&apos;s data</li>
              <li>Audit logging of all authentication and data access events</li>
              <li>Database access restricted to application layer only</li>
            </ul>
            <p className="mt-3">
              Despite these measures, no method of transmission over the internet is 100% secure.
              We cannot guarantee absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">5. Data Retention</h2>
            <ul className="list-disc list-inside space-y-1">
              <li>Account data: retained while your account is active</li>
              <li>API request logs: 30 days</li>
              <li>Audit logs: 12 months</li>
              <li>Deleted accounts: data removed within 30 days of deletion request</li>
              <li>Anonymised usage analytics: retained indefinitely</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">6. Third-Party Services</h2>
            <p className="mb-3">We use the following third-party services to operate the platform:</p>
            <div className="space-y-3">
              {[
                { name: 'Neon (PostgreSQL)', purpose: 'Database hosting', location: 'US East', policy: 'https://neon.tech/privacy' },
                { name: 'Upstash (Redis)', purpose: 'Session and rate-limit storage', location: 'US East', policy: 'https://upstash.com/trust/privacy.pdf' },
                { name: 'Render', purpose: 'Backend application hosting', location: 'United States', policy: 'https://render.com/privacy' },
                { name: 'Vercel', purpose: 'Frontend hosting', location: 'Global CDN', policy: 'https://vercel.com/legal/privacy-policy' },
                { name: 'Anthropic (optional)', purpose: 'AI intent analysis (when enabled)', location: 'United States', policy: 'https://www.anthropic.com/privacy' },
              ].map(({ name, purpose, location, policy }) => (
                <div key={name} className="bg-radar-800/30 rounded-lg p-3">
                  <p className="font-medium text-white text-xs">{name}</p>
                  <p className="text-radar-400 text-xs">{purpose} · {location}</p>
                  <a href={policy} target="_blank" rel="noopener noreferrer" className="text-radar-500 hover:text-radar-300 text-xs transition-colors">
                    Privacy policy →
                  </a>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">7. Your Rights</h2>
            <p className="mb-3">
              Depending on your location, you may have the following rights regarding your data:
            </p>
            <ul className="list-disc list-inside space-y-1 mb-4">
              <li><strong className="text-white">Access:</strong> Request a copy of the personal data we hold about you</li>
              <li><strong className="text-white">Correction:</strong> Request correction of inaccurate data</li>
              <li><strong className="text-white">Deletion:</strong> Request deletion of your account and associated data</li>
              <li><strong className="text-white">Portability:</strong> Request your data in a machine-readable format</li>
              <li><strong className="text-white">Objection:</strong> Object to processing of your data in certain circumstances</li>
              <li><strong className="text-white">Restriction:</strong> Request restriction of processing in certain circumstances</li>
            </ul>
            <p>
              To exercise any of these rights, email us at{' '}
              <a href={`mailto:${CONTACT_EMAIL}`} className="text-radar-400 hover:text-white transition-colors">
                {CONTACT_EMAIL}
              </a>. We will respond within 30 days.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">8. Cookies</h2>
            <p className="mb-3">
              We use minimal browser storage:
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong className="text-white">localStorage:</strong> Access and refresh tokens for authentication (cleared on logout)</li>
            </ul>
            <p className="mt-3">
              We do not use advertising cookies, third-party tracking cookies, or analytics
              cookies at this time.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">9. Children&apos;s Privacy</h2>
            <p>
              AI Intent Radar is not directed at children under 16 years of age. We do not
              knowingly collect personal information from children. If you believe we have
              inadvertently collected such information, please contact us immediately.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify registered
              users of material changes via email. The &quot;Last updated&quot; date at the top of this
              page reflects when changes were last made. Continued use of the platform after
              changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-white mb-3">11. Contact Us</h2>
            <p>
              For any privacy-related questions, requests, or complaints, please contact:
            </p>
            <div className="mt-3 bg-radar-800/30 rounded-lg p-4">
              <p className="text-white font-medium">{COMPANY_NAME}</p>
              <p className="text-radar-300 mt-1">
                Email:{' '}
                <a href={`mailto:${CONTACT_EMAIL}`} className="text-radar-400 hover:text-white transition-colors">
                  {CONTACT_EMAIL}
                </a>
              </p>
              <p className="text-radar-300">
                Website:{' '}
                <Link href="/contact" className="text-radar-400 hover:text-white transition-colors">
                  intentradar.ai/contact
                </Link>
              </p>
            </div>
          </section>

        </div>
      </div>

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

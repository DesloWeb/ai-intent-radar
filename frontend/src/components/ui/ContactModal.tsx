'use client';

import { useState, useCallback } from 'react';
import {
  X,
  ExternalLink,
  Mail,
  Search,
  Copy,
  CheckCircle,
  Phone,
} from 'lucide-react';
import { Opportunity } from '@/types';

interface ContactModalProps {
  opportunity: Opportunity;
  onClose: () => void;
  onContacted: () => void;
}

export function ContactModal({ opportunity: opp, onClose, onContacted }: ContactModalProps) {
  const [copied, setCopied] = useState(false);
  const [contacted, setContacted] = useState(false);

  // Build outreach message from opportunity intelligence
  const outreachSubject = `Re: ${opp.title.slice(0, 80)}`;
  const outreachBody = [
    `Hi,`,
    ``,
    `I came across your ${opp.category} opportunity and wanted to reach out.`,
    ``,
    opp.why_now ? `${opp.why_now}` : '',
    ``,
    opp.recommended_action ? `${opp.recommended_action}` : '',
    ``,
    `I'd love to discuss how we can help. Would you be available for a brief call this week?`,
    ``,
    `Best regards`,
  ].filter(line => line !== undefined).join('\n');

  const mailtoLink = `mailto:?subject=${encodeURIComponent(outreachSubject)}&body=${encodeURIComponent(outreachBody)}`;

  const buyerSearch = opp.buyer_organization
    ? `https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(opp.buyer_organization)}`
    : `https://www.google.com/search?q=${encodeURIComponent(opp.title)}`;

  const googleSearch = `https://www.google.com/search?q=${encodeURIComponent(
    opp.buyer_organization ? `${opp.buyer_organization} contact` : opp.title
  )}`;

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(outreachBody);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback — select text
    }
  }, [outreachBody]);

  const handleContacted = () => {
    setContacted(true);
    onContacted();
    setTimeout(onClose, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-100">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Contact Channels</h2>
            <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{opp.title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors ml-4 mt-0.5"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Channels */}
        <div className="p-6 space-y-3">

          {/* 1 — View original source */}
          {opp.source_url && (
            <a
              href={opp.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={handleContacted}
              className="flex items-center gap-4 p-4 rounded-xl border border-gray-200 hover:border-radar-400 hover:bg-radar-50 transition-colors group"
            >
              <div className="w-10 h-10 rounded-lg bg-radar-100 flex items-center justify-center flex-shrink-0 group-hover:bg-radar-200 transition-colors">
                <ExternalLink className="w-5 h-5 text-radar-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">View Original Source</p>
                <p className="text-xs text-gray-500 truncate mt-0.5">{opp.source_url}</p>
              </div>
              <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-radar-500 flex-shrink-0" />
            </a>
          )}

          {/* 2 — Email draft */}
          <a
            href={mailtoLink}
            onClick={handleContacted}
            className="flex items-center gap-4 p-4 rounded-xl border border-gray-200 hover:border-emerald-400 hover:bg-emerald-50 transition-colors group"
          >
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0 group-hover:bg-emerald-200 transition-colors">
              <Mail className="w-5 h-5 text-emerald-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Open Email Draft</p>
              <p className="text-xs text-gray-500 mt-0.5">Pre-filled subject and outreach message</p>
            </div>
          </a>

          {/* 3 — Copy outreach message */}
          <button
            onClick={handleCopy}
            className="w-full flex items-center gap-4 p-4 rounded-xl border border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-colors group text-left"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-200 transition-colors">
              {copied
                ? <CheckCircle className="w-5 h-5 text-blue-600" />
                : <Copy className="w-5 h-5 text-blue-600" />
              }
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">
                {copied ? 'Copied to clipboard!' : 'Copy Outreach Message'}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">Personalised message based on opportunity intelligence</p>
            </div>
          </button>

          {/* 4a — Find buyer on LinkedIn */}
          <a
            href={buyerSearch}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleContacted}
            className="flex items-center gap-4 p-4 rounded-xl border border-gray-200 hover:border-blue-600 hover:bg-blue-50 transition-colors group"
          >
            <div className="w-10 h-10 rounded-lg bg-[#0077B5]/10 flex items-center justify-center flex-shrink-0 group-hover:bg-[#0077B5]/20 transition-colors">
              <Search className="w-5 h-5 text-[#0077B5]" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Find on LinkedIn</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {opp.buyer_organization
                  ? `Search for ${opp.buyer_organization}`
                  : 'Search for the buyer or organisation'}
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-[#0077B5] flex-shrink-0" />
          </a>

          {/* 4b — Google search */}
          <a
            href={googleSearch}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleContacted}
            className="flex items-center gap-4 p-4 rounded-xl border border-gray-200 hover:border-orange-400 hover:bg-orange-50 transition-colors group"
          >
            <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0 group-hover:bg-orange-200 transition-colors">
              <Search className="w-5 h-5 text-orange-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Search Google</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {opp.buyer_organization
                  ? `Find contact info for ${opp.buyer_organization}`
                  : 'Find more information about this opportunity'}
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-orange-500 flex-shrink-0" />
          </a>
        </div>

        {/* Outreach message preview */}
        <div className="px-6 pb-6">
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
            <p className="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wide">Outreach message preview</p>
            <p className="text-xs text-gray-600 whitespace-pre-line leading-relaxed">{outreachBody}</p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 pb-6">
          {contacted ? (
            <div className="flex items-center justify-center gap-2 py-2.5 text-sm font-medium text-emerald-600">
              <CheckCircle className="w-4 h-4" />
              Marked as contacted
            </div>
          ) : (
            <button
              onClick={handleContacted}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-xl transition-colors"
            >
              <Phone className="w-4 h-4" />
              Mark as Contacted
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

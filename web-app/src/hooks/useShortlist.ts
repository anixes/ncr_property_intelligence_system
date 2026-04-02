import { useState, useEffect } from 'react';
import { PropertyListing } from '../types';

export function useShortlist() {
  const [shortlist, setShortlist] = useState<PropertyListing[]>([]);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('ncr_shortlist');
    if (saved) {
      try {
        setShortlist(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse shortlist:', e);
      }
    }
  }, []);

  const getPropertyId = (p: PropertyListing) => `${p.society}-${p.locality}-${p.price}-${p.area}-${p.bhk}`;

  const toggleShortlist = (property: PropertyListing) => {
    const propId = getPropertyId(property);
    const isPresent = shortlist.some(p => getPropertyId(p) === propId);
    let newList;
    if (isPresent) {
      newList = shortlist.filter(p => getPropertyId(p) !== propId);
    } else {
      newList = [...shortlist, property];
    }
    
    setShortlist(newList);
    localStorage.setItem('ncr_shortlist', JSON.stringify(newList));
  };

  const isInShortlist = (property: PropertyListing) => {
    return shortlist.some(p => getPropertyId(p) === getPropertyId(property));
  };

  return { shortlist, toggleShortlist, isInShortlist };
}

import { useState, useEffect, useCallback } from "react";

export interface CharacterStats {
  strength: number;
  agility: number;
  intelligence: number;
  charisma: number;
  luck: number;
  vitality: number;
}

export interface CharacterData {
  id: string;
  name: string;
  jobClassId: string;
  jobClass: string;
  level: number;
  imageUrl: string;
  stats: CharacterStats;
  description: string;
  createdAt: string;
}

const STORAGE_KEY = "character_history";
const MAX_HISTORY = 20;

export const useCharacterHistory = () => {
  const [history, setHistory] = useState<CharacterData[]>([]);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load character history:", error);
    }
  }, []);

  // Save history to localStorage
  const saveToStorage = useCallback((data: CharacterData[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error("Failed to save character history:", error);
    }
  }, []);

  // Add a new character to history
  const addCharacter = useCallback((character: Omit<CharacterData, "id" | "createdAt">) => {
    const newCharacter: CharacterData = {
      ...character,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };

    setHistory((prev) => {
      const updated = [newCharacter, ...prev].slice(0, MAX_HISTORY);
      saveToStorage(updated);
      return updated;
    });

    return newCharacter;
  }, [saveToStorage]);

  // Remove a character from history
  const removeCharacter = useCallback((id: string) => {
    setHistory((prev) => {
      const updated = prev.filter((char) => char.id !== id);
      saveToStorage(updated);
      return updated;
    });
  }, [saveToStorage]);

  // Clear all history
  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    history,
    addCharacter,
    removeCharacter,
    clearHistory,
  };
};

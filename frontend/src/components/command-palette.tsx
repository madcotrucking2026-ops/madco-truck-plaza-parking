"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Truck, Building2 } from "lucide-react";
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { api, type SearchResultItem } from "@/lib/api";
import { onOpenCommandPalette } from "@/lib/command-palette-events";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const router = useRouter();

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    const unsubscribe = onOpenCommandPalette(() => setOpen(true));
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timeout = setTimeout(() => {
      api
        .get<SearchResultItem[]>(`/api/search?q=${encodeURIComponent(query.trim())}`)
        .then(setResults)
        .catch(() => setResults([]));
    }, 200);
    return () => clearTimeout(timeout);
  }, [query]);

  function go(item: SearchResultItem) {
    setOpen(false);
    setQuery("");
    router.push(`/lot-check?q=${encodeURIComponent(item.query)}`);
  }

  const companies = results.filter((r) => r.type === "company");
  const vehicles = results.filter((r) => r.type === "vehicle");

  return (
    <CommandDialog
      open={open}
      onOpenChange={setOpen}
      title="Search Everywhere"
      description="Search trucks, trailers, license plates, companies, or phone numbers"
    >
      <Command shouldFilter={false}>
        <CommandInput
          placeholder="Search truck, trailer, license, company, phone…"
          value={query}
          onValueChange={setQuery}
        />
        <CommandList>
          {query.trim() && results.length === 0 && <CommandEmpty>No matches found.</CommandEmpty>}
          {vehicles.length > 0 && (
            <CommandGroup heading="Vehicles">
              {vehicles.map((item, i) => (
                <CommandItem key={`vehicle-${i}`} onSelect={() => go(item)}>
                  <Truck />
                  <span>{item.label}</span>
                  {item.sublabel && <span className="text-muted-foreground">{item.sublabel}</span>}
                </CommandItem>
              ))}
            </CommandGroup>
          )}
          {companies.length > 0 && (
            <CommandGroup heading="Companies">
              {companies.map((item, i) => (
                <CommandItem key={`company-${i}`} onSelect={() => go(item)}>
                  <Building2 />
                  <span>{item.label}</span>
                  {item.sublabel && <span className="text-muted-foreground">{item.sublabel}</span>}
                </CommandItem>
              ))}
            </CommandGroup>
          )}
        </CommandList>
      </Command>
    </CommandDialog>
  );
}

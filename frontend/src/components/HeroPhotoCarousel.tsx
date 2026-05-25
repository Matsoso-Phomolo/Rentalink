import { useEffect, useMemo, useState } from "react";

type HeroFolder = "villages" | "nul-campus" | "lines";

type HeroCategory = {
  title: string;
  folder: HeroFolder;
  fallback: string[];
  dotClass: string;
};

type HeroManifest = Partial<Record<HeroFolder, string[]>>;

const categories: HeroCategory[] = [
  { title: "Roma Village", folder: "villages", fallback: ["roma-village.jpg", "village-2.jpg", "village-3.jpg"], dotClass: "blue" },
  { title: "NUL Campus", folder: "nul-campus", fallback: ["nul-campus.jpg", "campus-2.jpg", "campus-3.jpg"], dotClass: "red" },
  { title: "Student accommodation", folder: "lines", fallback: ["roma-accommodation.jpg", "line-2.jpg", "line-3.jpg"], dotClass: "black" }
];

export function HeroPhotoCarousel() {
  const [manifest, setManifest] = useState<HeroManifest>({});
  const [activeCategoryIndex, setActiveCategoryIndex] = useState(0);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [showLabel, setShowLabel] = useState(true);
  const activeCategory = categories[activeCategoryIndex];
  const imageNames = useMemo(() => {
    const manifestImages = manifest[activeCategory.folder]?.filter(Boolean) ?? [];
    return manifestImages.length ? manifestImages : activeCategory.fallback;
  }, [activeCategory, manifest]);
  const currentImage = `/hero/${activeCategory.folder}/${imageNames[activeImageIndex % imageNames.length]}`;

  useEffect(() => {
    let isMounted = true;
    fetch(`/hero/manifest.json?v=${Date.now()}`, { cache: "no-store" })
      .then((response) => (response.ok ? response.json() as Promise<HeroManifest> : null))
      .then((loadedManifest) => {
        if (isMounted && loadedManifest) setManifest(loadedManifest);
      })
      .catch(() => {
        if (isMounted) setManifest({});
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setActiveImageIndex((value) => (value + 1) % imageNames.length);
      setShowLabel(true);
    }, 4800);
    return () => window.clearInterval(intervalId);
  }, [imageNames.length, activeCategoryIndex]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => setShowLabel(false), 2400);
    return () => window.clearTimeout(timeoutId);
  }, [activeCategoryIndex, activeImageIndex]);

  function switchCategory(index: number) {
    setActiveCategoryIndex(index);
    setActiveImageIndex(0);
    setShowLabel(true);
  }

  return (
    <div
      className="hero-photo-slot hero-photo-single"
      role="img"
      aria-label={`${activeCategory.title} hero photo ${activeImageIndex + 1} of ${imageNames.length}`}
      style={{ backgroundImage: `linear-gradient(135deg, rgba(8, 31, 28, 0.3), rgba(8, 31, 28, 0.76)), url("${currentImage}")` }}
    >
      <div className="hero-dot-switcher" aria-label="Hero photo categories">
        {categories.map((category, index) => (
          <button
            aria-label={`Show ${category.title}`}
            className={`hero-dot ${category.dotClass}${activeCategoryIndex === index ? " active" : ""}`}
            key={category.folder}
            type="button"
            onClick={() => switchCategory(index)}
          />
        ))}
      </div>
      <div className={`hero-photo-label${showLabel ? " visible" : ""}`}>
        <span>{activeCategory.title}</span>
      </div>
      <small className="hero-photo-counter">{activeImageIndex + 1}/{imageNames.length}</small>
    </div>
  );
}

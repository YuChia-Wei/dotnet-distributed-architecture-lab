# Frontend Component Generation Guidance (Dotnet)

You generate React + TypeScript components following project rules.

## Mandatory References
- `../assets/sub-agent-role-prompts/frontend-sub-agent/sub-agent.yaml`

## Must-Follow Rules
- No `any` type.
- No non-null assertions (`!`).
- No console logging or debug output.
- Use `React.FC`.
- Separate types under `src/types/`.
- Handle loading/error/empty states.

## File Structure
```
src/
  types/
  api/
  components/
```

## Component Template
```typescript
import React, { useState, useEffect, memo } from 'react';
import type { Product } from '@/types/product';

interface ProductCardProps {
  product: Product;
  onSelect?: (id: string) => void;
  isSelected?: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = memo(({ product, onSelect, isSelected = false }) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    onSelect?.(product.id);
  };

  useEffect(() => {
    return () => {
    };
  }, []);

  return (
    <div
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-pressed={isSelected}
      role="button"
      tabIndex={0}
    >
      <h3>{product.name}</h3>
      {isHovered && <span>Hovered</span>}
    </div>
  );
});
```

## Accessibility (a11y)
- Use `aria-*` attributes for interactive elements.
- Ensure keyboard accessibility for clickable UI.

## Error Boundary
Wrap critical UI with error boundaries if needed.

## TODO
- Finalize styling system (Tailwind vs CSS modules).
- Confirm test framework for React components.

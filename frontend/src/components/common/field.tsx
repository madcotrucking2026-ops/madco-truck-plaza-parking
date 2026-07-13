"use client";

import { Children, cloneElement, isValidElement, useId } from "react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

/**
 * A labelled form control.
 *
 * The label is wired to the control by generating an id here and handing it to
 * the first element child. This used to be written as:
 *
 *     isValidElement(children) ? cloneElement(children, { id }) : children
 *
 * which quietly did NOTHING whenever a field had more than one child — an input
 * plus a hint line, say — because `children` is then an array and isValidElement
 * is false. The label kept pointing at an id no element had, so tapping it focused
 * nothing and a screen reader announced the field as unlabelled. On /passes/issue
 * that hit Company and End Date; the same copy-pasted component was in five files.
 *
 * Walking the children and linking the first element makes the multi-child case
 * work, which is the case that was broken.
 */
export function Field({
  label,
  required,
  className,
  labelClassName,
  children,
}: {
  label: string;
  required?: boolean;
  className?: string;
  labelClassName?: string;
  children: React.ReactNode;
}) {
  const id = useId();

  const items = Children.toArray(children);
  const controlIndex = items.findIndex((child) => isValidElement(child));
  const control = items.map((child, i) =>
    i === controlIndex && isValidElement<{ id?: string }>(child) ? cloneElement(child, { id }) : child,
  );

  return (
    <div className={className}>
      <Label htmlFor={id} className={cn("mb-1.5 block text-[var(--cream-foreground)]/80", labelClassName)}>
        {label}
        {required && <span className="text-[var(--amber-ink)]"> *</span>}
      </Label>
      {control}
    </div>
  );
}

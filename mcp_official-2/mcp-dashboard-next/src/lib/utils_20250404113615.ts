import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Combine class names with Tailwind
export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// Format date to locale string
export function formatDate(
	date: string | Date,
	options: Intl.DateTimeFormatOptions = {}
): string {
	const defaultOptions: Intl.DateTimeFormatOptions = {
		year: "numeric",
		month: "short",
		day: "numeric",
	};

	const mergedOptions = { ...defaultOptions, ...options };
	return new Date(date).toLocaleDateString(undefined, mergedOptions);
}

// Format time to locale string
export function formatTime(
	date: string | Date,
	options: Intl.DateTimeFormatOptions = {}
): string {
	const defaultOptions: Intl.DateTimeFormatOptions = {
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
	};

	const mergedOptions = { ...defaultOptions, ...options };
	return new Date(date).toLocaleTimeString(undefined, mergedOptions);
}

// Format date and time to locale string
export function formatDateTime(
	date: string | Date,
	options: Intl.DateTimeFormatOptions = {}
): string {
	const defaultOptions: Intl.DateTimeFormatOptions = {
		year: "numeric",
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
	};

	const mergedOptions = { ...defaultOptions, ...options };
	return new Date(date).toLocaleString(undefined, mergedOptions);
}

// Format relative time (e.g., "2 hours ago")
export function formatRelativeTime(date: string | Date): string {
	const now = new Date();
	const then = new Date(date);
	const diffMs = now.getTime() - then.getTime();

	// Convert to seconds
	const diffSec = Math.floor(diffMs / 1000);

	// Less than a minute
	if (diffSec < 60) {
		return "just now";
	}

	// Less than an hour
	if (diffSec < 3600) {
		const minutes = Math.floor(diffSec / 60);
		return `${minutes} minute${minutes > 1 ? "s" : ""} ago`;
	}

	// Less than a day
	if (diffSec < 86400) {
		const hours = Math.floor(diffSec / 3600);
		return `${hours} hour${hours > 1 ? "s" : ""} ago`;
	}

	// Less than a week
	if (diffSec < 604800) {
		const days = Math.floor(diffSec / 86400);
		return `${days} day${days > 1 ? "s" : ""} ago`;
	}

	// Less than a month
	if (diffSec < 2592000) {
		const weeks = Math.floor(diffSec / 604800);
		return `${weeks} week${weeks > 1 ? "s" : ""} ago`;
	}

	// Less than a year
	if (diffSec < 31536000) {
		const months = Math.floor(diffSec / 2592000);
		return `${months} month${months > 1 ? "s" : ""} ago`;
	}

	// More than a year
	const years = Math.floor(diffSec / 31536000);
	return `${years} year${years > 1 ? "s" : ""} ago`;
}

// Truncate text with ellipsis
export function truncateText(text: string, maxLength: number): string {
	if (text.length <= maxLength) {
		return text;
	}

	return text.slice(0, maxLength) + "...";
}

// Generate random ID
export function generateId(prefix: string = ""): string {
	return `${prefix}${Math.random().toString(36).substring(2, 11)}`;
}

// Deep clone object
export function deepClone<T>(obj: T): T {
	return JSON.parse(JSON.stringify(obj));
}

// Debounce function
export function debounce<T extends (...args: unknown[]) => unknown>(
	func: T,
	wait: number
): (...args: Parameters<T>) => void {
	let timeout: NodeJS.Timeout | null = null;

	return function (...args: Parameters<T>): void {
		const later = () => {
			timeout = null;
			func(...args);
		};

		if (timeout) {
			clearTimeout(timeout);
		}

		timeout = setTimeout(later, wait);
	};
}

// Throttle function
export function throttle<T extends (...args: unknown[]) => unknown>(
	func: T,
	limit: number
): (...args: Parameters<T>) => void {
	let inThrottle: boolean = false;

	return function (...args: Parameters<T>): void {
		if (!inThrottle) {
			func(...args);
			inThrottle = true;
			setTimeout(() => {
				inThrottle = false;
			}, limit);
		}
	};
}

// Get status color based on status string
export function getStatusColor(status: string): string {
	switch (status.toLowerCase()) {
		case "online":
		case "active":
		case "completed":
		case "success":
			return "bg-green-500/10 text-green-500 border-green-500/30";
		case "offline":
		case "inactive":
		case "draft":
			return "bg-gray-500/10 text-gray-500 border-gray-500/30";
		case "error":
		case "failed":
		case "blocked":
			return "bg-red-500/10 text-red-500 border-red-500/30";
		case "warning":
		case "paused":
		case "on_hold":
			return "bg-yellow-500/10 text-yellow-500 border-yellow-500/30";
		case "in_progress":
		case "running":
			return "bg-blue-500/10 text-blue-500 border-blue-500/30";
		default:
			return "bg-gray-500/10 text-gray-500 border-gray-500/30";
	}
}

// Format file size
export function formatFileSize(bytes: number): string {
	if (bytes === 0) return "0 Bytes";

	const k = 1024;
	const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
	const i = Math.floor(Math.log(bytes) / Math.log(k));

	return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Parse error message from API response
export function parseErrorMessage(error: unknown): string {
	if (!error) {
		return "An unknown error occurred";
	}

	// Type guard for error with response property
	if (typeof error === "object" && error !== null && "response" in error) {
		const errorWithResponse = error as {
			response?: { data?: { message?: string } };
		};
		if (errorWithResponse.response?.data?.message) {
			return errorWithResponse.response.data.message;
		}
	}

	// Type guard for error with message property
	if (typeof error === "object" && error !== null && "message" in error) {
		const errorWithMessage = error as { message?: string };
		if (
			errorWithMessage.message &&
			typeof errorWithMessage.message === "string"
		) {
			return errorWithMessage.message;
		}
	}

	return "An error occurred";
}

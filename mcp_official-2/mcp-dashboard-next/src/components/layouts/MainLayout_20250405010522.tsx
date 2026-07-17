"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
	LayoutGrid,
	Network,
	Users,
	Workflow,
	MessageSquare,
	Settings,
	Menu,
	LogOut,
	Activity,
	AlertCircle,
	CheckCircle2,
	BarChart2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip";

interface NavLinkProps {
	href: string;
	icon: any; // Use any to avoid type issues
	name: string;
	onClick?: () => void;
	isActive?: boolean;
}

// NavLink component moved outside of MainLayout
const NavLink: React.FC<NavLinkProps> = ({
	href,
	icon: Icon,
	name,
	onClick,
	isActive,
}) => {
	const pathname = usePathname();
	const active = isActive ?? pathname === href;

	return (
		<Link
			href={href}
			onClick={onClick}
			className={cn(
				"flex items-center gap-3 rounded-lg px-3 py-2 transition-all",
				active
					? "bg-[#7ebab5]/10 text-[#7ebab5]"
					: "text-[#f6f5f5]/70 hover:bg-[#7ebab5]/5 hover:text-[#7ebab5]"
			)}>
			<Icon className='h-5 w-5' />
			<span>{name}</span>
			{active && (
				<div className='ml-auto h-1.5 w-1.5 rounded-full bg-[#7ebab5]' />
			)}
		</Link>
	);
};

interface MainLayoutProps {
	children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
	const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
	const [mcpServerStatus, setMcpServerStatus] = useState<
		"connected" | "disconnected" | "error"
	>("disconnected");

	// Check MCP server connection status
	useEffect(() => {
		const checkServerStatus = async () => {
			try {
				const response = await fetch("http://localhost:3002/health", {
					method: "GET",
					headers: { "Content-Type": "application/json" },
				});

				if (response.ok) {
					setMcpServerStatus("connected");
				} else {
					setMcpServerStatus("error");
				}
			} catch (error) {
				console.error("Error checking MCP server status:", error);
				setMcpServerStatus("disconnected");
			}
		};

		// Check status immediately
		checkServerStatus();

		// Then check every 30 seconds
		const interval = setInterval(checkServerStatus, 30000);

		return () => clearInterval(interval);
	}, []);

	const navigation = [
		{ name: "Dashboard", href: "/", icon: LayoutGrid },
		{ name: "Agents", href: "/agents", icon: Users },
		{ name: "Network", href: "/network", icon: Network },
		{ name: "Projects", href: "/projects", icon: Workflow },
		{ name: "Workflows", href: "/workflows", icon: Workflow },
		{ name: "Communications", href: "/communications", icon: MessageSquare },
		{ name: "Analytics", href: "/analytics", icon: Activity },
		{ name: "Metrics", href: "/metrics", icon: BarChart2 },
		{ name: "Settings", href: "/settings", icon: Settings },
	];

	return (
		<div className='flex min-h-screen bg-[#1f2022] text-[#f6f5f5]'>
			{/* Desktop Sidebar */}
			<aside className='hidden md:flex w-64 flex-col border-r border-[#7ebab5]/10 bg-[#1f2022]'>
				<div className='flex h-14 items-center border-b border-[#7ebab5]/10 px-4'>
					<h1 className='text-xl font-bold text-[#7ebab5]'>MCP Dashboard</h1>
				</div>
				<nav className='flex-1 overflow-auto p-4 space-y-2'>
					{navigation.map((item) => (
						<NavLink
							key={item.name}
							href={item.href}
							icon={item.icon}
							name={item.name}
						/>
					))}
				</nav>
				<div className='border-t border-[#7ebab5]/10 p-4 space-y-4'>
					{/* MCP Server Status */}
					<div className='flex items-center justify-between px-3 py-2 rounded-md bg-[#1f2022]/50'>
						<div className='flex items-center'>
							<Activity className='h-4 w-4 mr-2 text-[#7ebab5]' />
							<span className='text-sm text-[#f6f5f5]/70'>MCP Server</span>
						</div>
						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger asChild>
									<div>
										{mcpServerStatus === "connected" && (
											<Badge
												variant='outline'
												className='bg-green-500/10 text-green-500 border-green-500/20'>
												<CheckCircle2 className='h-3 w-3 mr-1' />
												Connected
											</Badge>
										)}
										{mcpServerStatus === "disconnected" && (
											<Badge
												variant='outline'
												className='bg-orange-500/10 text-orange-500 border-orange-500/20'>
												<AlertCircle className='h-3 w-3 mr-1' />
												Disconnected
											</Badge>
										)}
										{mcpServerStatus === "error" && (
											<Badge
												variant='outline'
												className='bg-red-500/10 text-red-500 border-red-500/20'>
												<AlertCircle className='h-3 w-3 mr-1' />
												Error
											</Badge>
										)}
									</div>
								</TooltipTrigger>
								<TooltipContent>
									<p>MCP Server Status: {mcpServerStatus}</p>
									<p className='text-xs text-[#f6f5f5]/50'>
										http://localhost:3002
									</p>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
					</div>

					<Button
						variant='outline'
						className='w-full justify-start text-[#f6f5f5]/70 hover:text-[#7ebab5] hover:bg-[#7ebab5]/5'>
						<LogOut className='mr-2 h-4 w-4' />
						Logout
					</Button>
				</div>
			</aside>

			{/* Mobile Menu - Content moved to header */}

			{/* Main Content */}
			<div className='flex flex-1 flex-col'>
				{/* Mobile Header */}
				<header className='flex h-14 items-center border-b border-[#7ebab5]/10 bg-[#1f2022] px-4 md:hidden'>
					<Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
						<SheetTrigger asChild>
							<Button variant='ghost' size='icon' className='mr-2'>
								<Menu className='h-5 w-5 text-[#7ebab5]' />
								<span className='sr-only'>Toggle menu</span>
							</Button>
						</SheetTrigger>
						<SheetContent
							side='left'
							className='w-64 p-0 bg-[#1f2022] border-r border-[#7ebab5]/10'>
							<div className='flex h-14 items-center border-b border-[#7ebab5]/10 px-4'>
								<h1 className='text-xl font-bold text-[#7ebab5]'>
									MCP Dashboard
								</h1>
							</div>
							<nav className='flex-1 overflow-auto p-4 space-y-2'>
								{navigation.map((item) => (
									<NavLink
										key={item.name}
										href={item.href}
										icon={item.icon}
										name={item.name}
										onClick={() => setIsMobileMenuOpen(false)}
									/>
								))}
							</nav>
							<div className='border-t border-[#7ebab5]/10 p-4 space-y-4'>
								{/* MCP Server Status */}
								<div className='flex items-center justify-between px-3 py-2 rounded-md bg-[#1f2022]/50'>
									<div className='flex items-center'>
										<Activity className='h-4 w-4 mr-2 text-[#7ebab5]' />
										<span className='text-sm text-[#f6f5f5]/70'>
											MCP Server
										</span>
									</div>
									<TooltipProvider>
										<Tooltip>
											<TooltipTrigger asChild>
												<div>
													{mcpServerStatus === "connected" && (
														<Badge
															variant='outline'
															className='bg-green-500/10 text-green-500 border-green-500/20'>
															<CheckCircle2 className='h-3 w-3 mr-1' />
															Connected
														</Badge>
													)}
													{mcpServerStatus === "disconnected" && (
														<Badge
															variant='outline'
															className='bg-orange-500/10 text-orange-500 border-orange-500/20'>
															<AlertCircle className='h-3 w-3 mr-1' />
															Disconnected
														</Badge>
													)}
													{mcpServerStatus === "error" && (
														<Badge
															variant='outline'
															className='bg-red-500/10 text-red-500 border-red-500/20'>
															<AlertCircle className='h-3 w-3 mr-1' />
															Error
														</Badge>
													)}
												</div>
											</TooltipTrigger>
											<TooltipContent>
												<p>MCP Server Status: {mcpServerStatus}</p>
												<p className='text-xs text-[#f6f5f5]/50'>
													http://localhost:3002
												</p>
											</TooltipContent>
										</Tooltip>
									</TooltipProvider>
								</div>

								<Button
									variant='outline'
									className='w-full justify-start text-[#f6f5f5]/70 hover:text-[#7ebab5] hover:bg-[#7ebab5]/5'>
									<LogOut className='mr-2 h-4 w-4' />
									Logout
								</Button>
							</div>
						</SheetContent>
					</Sheet>
					<h1 className='text-lg font-bold text-[#7ebab5]'>MCP Dashboard</h1>
				</header>

				{/* Page Content */}
				<main className='flex-1 overflow-auto p-4 md:p-6'>{children}</main>
			</div>
		</div>
	);
};

export default MainLayout;

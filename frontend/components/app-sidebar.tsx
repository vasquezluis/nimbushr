"use client";

import { formatDistanceToNow } from "date-fns";
import {
  Bot,
  Clock,
  MessageSquare,
  MoreHorizontal,
  Plus,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

interface Conversation {
  id: string;
  title: string;
  timestamp: Date;
  preview: string;
}

export function AppSidebar() {
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: "1",
      title: "Employee Benefits Overview",
      timestamp: new Date(Date.now() - 3600000),
      preview: "What are the health insurance options?",
    },
    {
      id: "2",
      title: "Remote Work Policy",
      timestamp: new Date(Date.now() - 7200000),
      preview: "Can I work from home?",
    },
    {
      id: "3",
      title: "Vacation Days Inquiry",
      timestamp: new Date(Date.now() - 86400000),
      preview: "How many vacation days do I get?",
    },
    {
      id: "4",
      title: "Performance Review Process",
      timestamp: new Date(Date.now() - 172800000),
      preview: "When are performance reviews?",
    },
    {
      id: "5",
      title: "Training Opportunities",
      timestamp: new Date(Date.now() - 259200000),
      preview: "What training programs are available?",
    },
  ]);

  const [activeId, setActiveId] = useState("1");

  const handleNewChat = () => {
    const newId = (conversations.length + 1).toString();
    const newConversation: Conversation = {
      id: newId,
      title: "New Conversation",
      timestamp: new Date(),
      preview: "Start a new conversation...",
    };
    setConversations([newConversation, ...conversations]);
    setActiveId(newId);
  };

  const handleDelete = (id: string) => {
    setConversations(conversations.filter((c) => c.id !== id));
    if (activeId === id && conversations.length > 0) {
      setActiveId(conversations[0].id);
    }
  };

  // Group conversations by time
  const today = conversations.filter(
    (c) => Date.now() - c.timestamp.getTime() < 86400000,
  );
  const yesterday = conversations.filter(
    (c) =>
      Date.now() - c.timestamp.getTime() >= 86400000 &&
      Date.now() - c.timestamp.getTime() < 172800000,
  );
  const older = conversations.filter(
    (c) => Date.now() - c.timestamp.getTime() >= 172800000,
  );

  const renderConversationGroup = (convos: Conversation[], label: string) => {
    if (convos.length === 0) return null;

    return (
      <SidebarGroup>
        <SidebarGroupLabel className="text-white/40 text-xs font-medium px-2">
          {label}
        </SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            {convos.map((conversation) => {
              const isActive = conversation.id === activeId;
              return (
                <SidebarMenuItem key={conversation.id}>
                  <SidebarMenuButton
                    onClick={() => setActiveId(conversation.id)}
                    isActive={isActive}
                    className={`
                      group relative px-3 py-2.5
                      ${
                        isActive
                          ? "bg-white/10 hover:bg-white/15 border border-white/20"
                          : "hover:bg-white/5"
                      }
                    `}
                  >
                    <div className="flex items-start gap-3 w-full min-w-0">
                      <div
                        className={`
                          mt-0.5 rounded-md p-1.5
                          ${
                            isActive
                              ? "bg-white/20"
                              : "bg-white/10 group-hover:bg-white/15"
                          }
                          transition-colors shrink-0
                        `}
                      >
                        <MessageSquare className="h-3.5 w-3.5 text-white/60" />
                      </div>

                      <div className="flex-1 min-w-0 space-y-0.5">
                        <h3 className="text-sm font-medium text-white/90 truncate">
                          {conversation.title}
                        </h3>
                        <p className="text-xs text-white/40 truncate">
                          {conversation.preview}
                        </p>
                        <div className="flex items-center gap-1 text-xs text-white/30">
                          <Clock className="h-3 w-3" />
                          <span className="truncate">
                            {formatDistanceToNow(conversation.timestamp, {
                              addSuffix: true,
                            })}
                          </span>
                        </div>
                      </div>
                    </div>
                  </SidebarMenuButton>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <SidebarMenuAction
                        showOnHover
                        className="hover:bg-white/10"
                      >
                        <MoreHorizontal className="h-4 w-4 text-white/60" />
                        <span className="sr-only">More</span>
                      </SidebarMenuAction>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent
                      side="right"
                      align="start"
                      className="bg-[#1A1A1A] border-white/10"
                    >
                      <DropdownMenuItem
                        onClick={() => handleDelete(conversation.id)}
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10 focus:bg-red-500/10 focus:text-red-300 cursor-pointer"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        <span>Delete</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </SidebarMenuItem>
              );
            })}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  };

  return (
    <Sidebar className="border-r border-white/5 bg-[#0F0F0F]">
      <SidebarHeader className="border-b border-white/5 px-4 py-4">
        <div className="space-y-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-linear-to-br from-white/10 to-white/5 border border-white/10">
                <Bot className="h-4 w-4 text-white/70" />
              </div>
              <h1 className="text-lg font-bold bg-linear-to-r from-white via-white/90 to-white/60 bg-clip-text text-transparent">
                RAG Assistant
              </h1>
            </div>
            <p className="text-xs text-white/40 pl-0.5">
              AI-powered document insights
            </p>
          </div>

          <Button
            onClick={handleNewChat}
            className="w-full h-10 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg transition-all duration-200 group"
          >
            <Plus className="h-4 w-4 mr-2 text-white/70 group-hover:text-white transition-colors" />
            <span className="text-white/90 text-sm font-medium">New Chat</span>
          </Button>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2 py-2">
        {renderConversationGroup(today, "Today")}
        {renderConversationGroup(yesterday, "Yesterday")}
        {renderConversationGroup(older, "Previous 7 Days")}
      </SidebarContent>

      <SidebarFooter className="border-t border-white/5 p-4">
        <div className="text-xs text-white/30 text-center space-y-0.5">
          <p className="font-medium">Powered by RAG</p>
          <p>Intelligent document retrieval</p>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}

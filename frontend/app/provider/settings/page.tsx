"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import apiClient from "@/lib/api/client";

interface User {
    id: string;
    email: string;
    full_name: string;
    role: string;
    tenant_id: string;
}

export default function SettingsPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [currentUser, setCurrentUser] = useState<User | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [userData, usersData] = await Promise.all([
                apiClient.getCurrentUser(),
                apiClient.getUsers()
            ]);
            setCurrentUser(userData);
            setUsers(usersData);
        } catch (error) {
            console.error("Failed to load settings data", error);
        } finally {
            setLoading(false);
        }
    };

    const handleRoleUpdate = async (userId: string, newRole: string) => {
        try {
            await apiClient.updateUserRole(userId, newRole);
            // Refresh list
            const usersData = await apiClient.getUsers();
            setUsers(usersData);
        } catch (error) {
            console.error("Failed to update role", error);
        }
    };

    return (
        <div className="container mx-auto py-10">
            <h1 className="text-3xl font-bold mb-6">Settings</h1>

            <Tabs defaultValue="profile" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="profile">Profile</TabsTrigger>
                    <TabsTrigger value="organization">Organization</TabsTrigger>
                    <TabsTrigger value="team">Team Members</TabsTrigger>
                </TabsList>

                <TabsContent value="profile">
                    <Card>
                        <CardHeader>
                            <CardTitle>Profile Settings</CardTitle>
                            <CardDescription>Manage your personal information.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Full Name</Label>
                                <Input id="name" defaultValue={currentUser?.full_name} disabled />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input id="email" defaultValue={currentUser?.email} disabled />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="role">Role</Label>
                                <Input id="role" defaultValue={currentUser?.role} disabled />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="organization">
                    <Card>
                        <CardHeader>
                            <CardTitle>Organization Settings</CardTitle>
                            <CardDescription>Manage your organization details.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Organization Name</Label>
                                <Input defaultValue="Antigravity Healthcare" disabled />
                            </div>
                            <div className="space-y-2">
                                <Label>Subscription Plan</Label>
                                <Input defaultValue="Professional" disabled />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="team">
                    <Card>
                        <CardHeader>
                            <CardTitle>Team Management</CardTitle>
                            <CardDescription>Manage users and their roles within your organization.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="rounded-md border">
                                <table className="w-full text-sm">
                                    <thead className="bg-muted/50">
                                        <tr>
                                            <th className="p-4 text-left font-medium">Name</th>
                                            <th className="p-4 text-left font-medium">Email</th>
                                            <th className="p-4 text-left font-medium">Role</th>
                                            <th className="p-4 text-left font-medium">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {users.map((user) => (
                                            <tr key={user.id} className="border-t">
                                                <td className="p-4">{user.full_name}</td>
                                                <td className="p-4">{user.email}</td>
                                                <td className="p-4">
                                                    <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                                        {user.role}
                                                    </span>
                                                </td>
                                                <td className="p-4">
                                                    <Select
                                                        defaultValue={user.role}
                                                        onValueChange={(value) => handleRoleUpdate(user.id, value)}
                                                        disabled={currentUser?.role !== 'admin' && currentUser?.role !== 'super_admin'}
                                                    >
                                                        <SelectTrigger className="w-[140px]">
                                                            <SelectValue placeholder="Select role" />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="admin">Admin</SelectItem>
                                                            <SelectItem value="doctor">Doctor</SelectItem>
                                                            <SelectItem value="nurse">Nurse</SelectItem>
                                                            <SelectItem value="staff">Staff</SelectItem>
                                                            <SelectItem value="patient">Patient</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}

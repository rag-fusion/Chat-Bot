import { useState, useEffect, useRef } from "react";
import { X, Camera } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./ui/dialog";
import { API_BASE_URL } from "../config";

export default function ProfileModal({ isOpen, onClose, user, onSave, isDarkMode }) {
  const [displayName, setDisplayName] = useState(user?.full_name || "");
  const [username, setUsername] = useState(user?.username || user?.email?.split('@')[0] || "");
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);

  // Sync state when user prop changes or modal opens
  useEffect(() => {
    if (isOpen && user) {
        setDisplayName(user.full_name || "");
        setUsername(user.username || user.email?.split('@')[0] || "");
        setAvatarPreview(null); // Reset preview when modal opens
    }
  }, [isOpen, user]);

  // Clean up object URL on unmount or when preview changes
  useEffect(() => {
    return () => {
      if (avatarPreview) {
        URL.revokeObjectURL(avatarPreview);
      }
    };
  }, [avatarPreview]);

  const handleSave = async () => {
    setIsLoading(true);
    const token = localStorage.getItem("token");
    
    try {
        let updatedUser = { ...user, full_name: displayName, username: username };
        let hasChanges = false;

        // 1. Upload Avatar if changed (we don't track explicit change yet, but checking if ref has file)
        // Actually, we should track if a file was selected.
        // Let's use a state for selectedFile
        if (selectedFile) {
            const formData = new FormData();
            formData.append("file", selectedFile);
            
            const res = await fetch(`${API_BASE_URL}/api/auth/profile/avatar`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            
            if (!res.ok) throw new Error("Failed to upload avatar");
            const data = await res.json();
            updatedUser.avatar_url = data.avatar_url;
            hasChanges = true;
        }

        // 2. Update Profile Info
        if (displayName !== user.full_name || username !== user.username) {
            const res = await fetch(`${API_BASE_URL}/api/auth/profile`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ full_name: displayName, username: username })
            });

            if (!res.ok) throw new Error("Failed to update profile");
            const data = await res.json();
            // Merge response
            updatedUser = { ...updatedUser, ...data };
            hasChanges = true;
        }

        if (hasChanges) {
             await onSave(updatedUser);
        }
        
        onClose();
    } catch (e) {
        console.error("Failed to save profile", e);
    } finally {
        setIsLoading(false);
    }
  };

  const [selectedFile, setSelectedFile] = useState(null);

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const previewUrl = URL.createObjectURL(file);
      setAvatarPreview(previewUrl);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`sm:max-w-[400px] p-6 rounded-xl border ${isDarkMode ? "bg-gray-800 border-gray-700 text-gray-100" : "bg-white border-gray-200 text-gray-900"}`}>
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-semibold">Edit profile</DialogTitle>
          <DialogDescription className="text-sm text-gray-500">Update your profile details.</DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-6">
            {/* Avatar Section */}
            <div className="flex justify-center">
                <div className="relative group cursor-pointer" onClick={handleAvatarClick}>
                    <div className="w-24 h-24 rounded-full bg-[#A3B18A] flex items-center justify-center text-4xl text-white font-normal overflow-hidden">
                        {avatarPreview ? (
                            <img src={avatarPreview} alt="Avatar Preview" className="w-full h-full object-cover" />
                        ) : (user?.avatar_url ? (
                            <img src={`${API_BASE_URL}${user.avatar_url}`} alt="Avatar" className="w-full h-full object-cover" />
                        ) : (
                            displayName ? (displayName.length > 1 ? displayName.substring(0,2).toUpperCase() : displayName[0].toUpperCase()) : "U"
                        ))}
                    </div>
                    <div className="absolute bottom-0 right-0 p-2 bg-gray-800 rounded-full border-2 border-transparent group-hover:bg-gray-700 transition-colors">
                        <Camera className="w-4 h-4 text-white" />
                    </div>
                </div>
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    accept="image/*"
                    onChange={handleFileChange}
                />
            </div>

            {/* Inputs */}
            <div className="space-y-4">
                <div className="space-y-2">
                    <label className={`text-sm font-medium ${isDarkMode ? "text-gray-300" : "text-gray-700"}`}>
                        Display name
                    </label>
                    <input 
                        type="text" 
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        className={`w-full px-3 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 outline-none transition-all ${isDarkMode ? "bg-black/20 border-gray-600 focus:border-blue-500 text-white placeholder-gray-500" : "bg-white border-gray-300 focus:border-blue-500 text-gray-900 placeholder-gray-400"}`}
                        placeholder="Enter your name"
                    />
                </div>

                <div className="space-y-2">
                    <label className={`text-sm font-medium ${isDarkMode ? "text-gray-300" : "text-gray-700"}`}>
                        Username
                    </label>
                    <input 
                        type="text" 
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className={`w-full px-3 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 outline-none transition-all ${isDarkMode ? "bg-black/20 border-gray-600 focus:border-blue-500 text-white placeholder-gray-500" : "bg-white border-gray-300 focus:border-blue-500 text-gray-900 placeholder-gray-400"}`}
                        placeholder="Enter your username"
                    />
                    <p className={`text-xs ${isDarkMode ? "text-gray-500" : "text-gray-500"}`}>
                        Your profile helps people recognize you. Your name and username are also used in the Sora app.
                    </p>
                </div>
            </div>

            {/* Footer Buttons */}
            <div className="flex justify-end gap-3 mt-2">
                <button 
                    onClick={onClose}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${isDarkMode ? "bg-gray-700 hover:bg-gray-600 text-white" : "bg-gray-100 hover:bg-gray-200 text-gray-900"}`}
                >
                    Cancel
                </button>
                <button 
                    onClick={handleSave}
                    disabled={isLoading}
                    className={`px-6 py-2 rounded-full text-sm font-medium text-black bg-white hover:bg-gray-100 transition-colors disabled:opacity-50 ${!isDarkMode && "bg-black text-white hover:bg-gray-800"}`} // Inverted colors for primary action usually? The image has white button "Save" on dark mode.
                >
                    {isLoading ? "Saving..." : "Save"}
                </button>
            </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

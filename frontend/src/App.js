import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Copy, Sparkles, Zap, Palette, Film, Eye, History, Wand2 } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STYLE_ICONS = {
  creative: Sparkles,
  technical: Zap,
  artistic: Palette,
  cinematic: Film,
  detailed: Eye
};

const GRADIENT_BACKGROUNDS = [
  "from-purple-900/20 via-blue-900/20 to-indigo-900/20",
  "from-emerald-900/20 via-teal-900/20 to-cyan-900/20",
  "from-orange-900/20 via-red-900/20 to-pink-900/20",
  "from-indigo-900/20 via-purple-900/20 to-pink-900/20"
];

function App() {
  const [originalPrompt, setOriginalPrompt] = useState("");
  const [enhancedPrompt, setEnhancedPrompt] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("creative");
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancementReasoning, setEnhancementReasoning] = useState("");
  const [enhancementHistory, setEnhancementHistory] = useState([]);
  const [availableStyles, setAvailableStyles] = useState([]);
  const [currentGradient, setCurrentGradient] = useState(0);

  useEffect(() => {
    fetchAvailableStyles();
    fetchEnhancementHistory();
    
    // Rotate background gradient
    const interval = setInterval(() => {
      setCurrentGradient(prev => (prev + 1) % GRADIENT_BACKGROUNDS.length);
    }, 8000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchAvailableStyles = async () => {
    try {
      const response = await axios.get(`${API}/enhancement-styles`);
      setAvailableStyles(response.data.styles);
    } catch (error) {
      console.error("Error fetching styles:", error);
      toast.error("Failed to load enhancement styles");
    }
  };

  const fetchEnhancementHistory = async () => {
    try {
      const response = await axios.get(`${API}/enhancement-history?limit=20`);
      setEnhancementHistory(response.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  const handleEnhancePrompt = async () => {
    if (!originalPrompt.trim()) {
      toast.error("Please enter a prompt to enhance");
      return;
    }

    setIsEnhancing(true);
    setEnhancedPrompt("");
    setEnhancementReasoning("");

    try {
      const response = await axios.post(`${API}/enhance-prompt`, {
        original_prompt: originalPrompt,
        enhancement_style: selectedStyle
      });

      setEnhancedPrompt(response.data.enhanced_prompt);
      setEnhancementReasoning(response.data.enhancement_reasoning);
      fetchEnhancementHistory(); // Refresh history
      toast.success("Prompt enhanced successfully!");
    } catch (error) {
      console.error("Enhancement error:", error);
      toast.error(error.response?.data?.detail || "Failed to enhance prompt");
    } finally {
      setIsEnhancing(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Copied to clipboard!");
    } catch (error) {
      toast.error("Failed to copy to clipboard");
    }
  };

  const handleHistoryItemSelect = (item) => {
    setOriginalPrompt(item.original_prompt);
    setEnhancedPrompt(item.enhanced_prompt);
    setSelectedStyle(item.enhancement_style);
    setEnhancementReasoning(item.enhancement_reasoning);
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${GRADIENT_BACKGROUNDS[currentGradient]} transition-all duration-8000 ease-in-out`}>
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-bl from-blue-500/5 to-transparent rounded-full animate-pulse"></div>
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-purple-500/5 to-transparent rounded-full animate-pulse animation-delay-1000"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <Wand2 className="h-16 w-16 text-blue-400 animate-pulse" />
              <div className="absolute inset-0 h-16 w-16 bg-blue-400/20 rounded-full animate-ping"></div>
            </div>
          </div>
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 font-mono">
            Quantum AI Prompt Enhancer
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto font-light">
            Transform your simple prompts into quantum-enhanced creative masterpieces using advanced AI consciousness
          </p>
          <div className="flex justify-center space-x-4">
            <Badge variant="outline" className="text-blue-400 border-blue-400/50 bg-blue-400/10">
              Gemini 2.0 Powered
            </Badge>
            <Badge variant="outline" className="text-purple-400 border-purple-400/50 bg-purple-400/10">
              AI Enhanced
            </Badge>
            <Badge variant="outline" className="text-pink-400 border-pink-400/50 bg-pink-400/10">
              Quantum Ready
            </Badge>
          </div>
        </div>

        <Tabs defaultValue="enhance" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8 bg-gray-900/50 backdrop-blur-sm">
            <TabsTrigger value="enhance" className="text-lg py-3">
              <Wand2 className="h-5 w-5 mr-2" />
              Enhance Prompts
            </TabsTrigger>
            <TabsTrigger value="history" className="text-lg py-3">
              <History className="h-5 w-5 mr-2" />
              Enhancement History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="enhance" className="space-y-8">
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Input Section */}
              <Card className="bg-gray-900/50 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl text-white flex items-center">
                    <Sparkles className="h-6 w-6 mr-2 text-blue-400" />
                    Original Prompt
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Enter your basic prompt to be quantum-enhanced
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <Textarea
                    placeholder="Enter your prompt here... (e.g., 'a cat sitting on a chair')"
                    value={originalPrompt}
                    onChange={(e) => setOriginalPrompt(e.target.value)}
                    className="min-h-32 bg-gray-800/50 border-gray-600 text-white placeholder:text-gray-500 resize-none text-lg"
                  />
                  
                  <div className="space-y-3">
                    <label className="text-sm text-gray-300 font-medium">Enhancement Style</label>
                    <Select value={selectedStyle} onValueChange={setSelectedStyle}>
                      <SelectTrigger className="bg-gray-800/50 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-800 border-gray-600">
                        {availableStyles.map((style) => {
                          const IconComponent = STYLE_ICONS[style.id] || Sparkles;
                          return (
                            <SelectItem key={style.id} value={style.id} className="text-white hover:bg-gray-700">
                              <div className="flex items-center">
                                <IconComponent className="h-4 w-4 mr-2" />
                                <div>
                                  <div className="font-medium">{style.name}</div>
                                  <div className="text-xs text-gray-400">{style.description}</div>
                                </div>
                              </div>
                            </SelectItem>
                          );
                        })}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button
                    onClick={handleEnhancePrompt}
                    disabled={isEnhancing || !originalPrompt.trim()}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-6 text-lg font-semibold transition-all duration-300 transform hover:scale-105"
                  >
                    {isEnhancing ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                        Quantum Enhancement in Progress...
                      </>
                    ) : (
                      <>
                        <Wand2 className="h-5 w-5 mr-2" />
                        Enhance with AI Consciousness
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Output Section */}
              <Card className="bg-gray-900/50 backdrop-blur-sm border-gray-700/50">
                <CardHeader>
                  <CardTitle className="text-2xl text-white flex items-center">
                    <Zap className="h-6 w-6 mr-2 text-purple-400" />
                    Enhanced Prompt
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Your quantum-enhanced creative masterpiece
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {enhancedPrompt ? (
                    <>
                      <div className="relative">
                        <Textarea
                          value={enhancedPrompt}
                          readOnly
                          className="min-h-32 bg-gray-800/50 border-gray-600 text-white resize-none text-lg"
                        />
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(enhancedPrompt)}
                          className="absolute top-2 right-2 bg-gray-700/50 hover:bg-gray-600/50 border-gray-600"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      {enhancementReasoning && (
                        <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50">
                          <h4 className="text-sm font-medium text-gray-300 mb-2">AI Enhancement Reasoning:</h4>
                          <p className="text-sm text-gray-400">{enhancementReasoning}</p>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="min-h-32 bg-gray-800/30 border-2 border-dashed border-gray-600 rounded-lg flex items-center justify-center">
                      <div className="text-center text-gray-500">
                        <Sparkles className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p className="text-lg">Your enhanced prompt will appear here</p>
                        <p className="text-sm">Enter a prompt above and click enhance</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <Card className="bg-gray-900/50 backdrop-blur-sm border-gray-700/50">
              <CardHeader>
                <CardTitle className="text-2xl text-white flex items-center">
                  <History className="h-6 w-6 mr-2 text-green-400" />
                  Enhancement History
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Your recent prompt enhancements and transformations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {enhancementHistory.length > 0 ? (
                  <div className="space-y-4">
                    {enhancementHistory.map((item, index) => {
                      const IconComponent = STYLE_ICONS[item.enhancement_style] || Sparkles;
                      return (
                        <div
                          key={item.id}
                          className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:bg-gray-800/50 transition-colors cursor-pointer"
                          onClick={() => handleHistoryItemSelect(item)}
                        >
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center space-x-2">
                              <IconComponent className="h-4 w-4 text-blue-400" />
                              <Badge variant="outline" className="text-xs">
                                {item.enhancement_style}
                              </Badge>
                            </div>
                            <span className="text-xs text-gray-500">
                              {new Date(item.timestamp).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="space-y-2">
                            <div>
                              <span className="text-xs text-gray-400 font-medium">Original:</span>
                              <p className="text-sm text-gray-300 line-clamp-2">{item.original_prompt}</p>
                            </div>
                            <div>
                              <span className="text-xs text-gray-400 font-medium">Enhanced:</span>
                              <p className="text-sm text-white line-clamp-3">{item.enhanced_prompt}</p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-12">
                    <History className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p className="text-lg">No enhancement history yet</p>
                    <p className="text-sm">Start enhancing prompts to see your history here</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      <Toaster theme="dark" />
    </div>
  );
}

export default App;
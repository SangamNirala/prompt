import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Progress } from './components/ui/progress';
import { Separator } from './components/ui/separator';
import { Alert, AlertDescription } from './components/ui/alert';
import { Loader2, Sparkles, Palette, Download, Eye, Zap, Target, Lightbulb, Rocket } from 'lucide-react';
import { toast, Toaster } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [businessInput, setBusinessInput] = useState({
    business_name: '',
    business_description: '',
    industry: '',
    target_audience: '',
    business_values: [],
    preferred_style: 'modern',
    preferred_colors: 'flexible'
  });
  const [currentProject, setCurrentProject] = useState(null);
  const [brandStrategy, setBrandStrategy] = useState(null);
  const [generatedAssets, setGeneratedAssets] = useState([]);
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState('business-info');

  const steps = [
    { id: 'business-info', title: 'Business Information', icon: Target },
    { id: 'brand-strategy', title: 'AI Brand Strategy', icon: Lightbulb },
    { id: 'visual-assets', title: 'Visual Assets', icon: Palette },
    { id: 'complete-package', title: 'Complete Package', icon: Rocket }
  ];

  const industries = [
    'Technology', 'Healthcare', 'Finance', 'Education', 'Retail', 'Food & Beverage',
    'Fashion', 'Real Estate', 'Consulting', 'Manufacturing', 'Entertainment', 'Other'
  ];

  const styleOptions = [
    'modern', 'minimalist', 'classic', 'playful', 'elegant', 'bold', 'rustic', 'luxury'
  ];

  const colorOptions = [
    'flexible', 'warm tones', 'cool tones', 'earth tones', 'bold colors', 'monochrome', 'pastels'
  ];

  const handleInputChange = (field, value) => {
    setBusinessInput(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleValuesChange = (value) => {
    const values = value.split(',').map(v => v.trim()).filter(v => v);
    setBusinessInput(prev => ({
      ...prev,
      business_values: values
    }));
  };

  const createProject = async () => {
    try {
      setIsGenerating(true);
      setProgress(10);
      
      const response = await axios.post(`${API}/projects`, businessInput);
      setCurrentProject(response.data);
      setProgress(25);
      
      toast.success('Project created successfully!');
      setActiveTab('brand-strategy');
      setCurrentStep(1);
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateBrandStrategy = async () => {
    if (!currentProject) return;
    
    try {
      setIsGenerating(true);
      setProgress(30);
      
      const response = await axios.post(`${API}/projects/${currentProject.id}/strategy`);
      setBrandStrategy(response.data);
      setProgress(50);
      
      toast.success('Brand strategy generated!');
      setActiveTab('visual-assets');
      setCurrentStep(2);
    } catch (error) {
      console.error('Error generating brand strategy:', error);
      toast.error('Failed to generate brand strategy. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateSingleAsset = async (assetType, context = '') => {
    if (!currentProject) return;
    
    try {
      setIsGenerating(true);
      
      const response = await axios.post(
        `${API}/projects/${currentProject.id}/assets/${assetType}`,
        null,
        { params: { context } }
      );
      
      setGeneratedAssets(prev => [...prev, response.data]);
      toast.success(`${assetType} generated successfully!`);
    } catch (error) {
      console.error(`Error generating ${assetType}:`, error);
      toast.error(`Failed to generate ${assetType}. Please try again.`);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateCompletePackage = async () => {
    if (!currentProject) return;
    
    try {
      setIsGenerating(true);
      setProgress(60);
      
      const response = await axios.post(`${API}/projects/${currentProject.id}/complete-package`);
      setGeneratedAssets(response.data.generated_assets);
      setProgress(100);
      
      toast.success('Complete brand package generated!');
      setActiveTab('complete-package');
      setCurrentStep(3);
    } catch (error) {
      console.error('Error generating complete package:', error);
      toast.error('Failed to generate complete package. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadAsset = (asset) => {
    const link = document.createElement('a');
    link.href = asset.asset_url;
    link.download = `${businessInput.business_name}-${asset.asset_type}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const BusinessInfoForm = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label htmlFor="business_name">Business Name *</Label>
          <Input
            id="business_name"
            placeholder="Enter your business name"
            value={businessInput.business_name}
            onChange={(e) => handleInputChange('business_name', e.target.value)}
            className="w-full"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="industry">Industry *</Label>
          <Select value={businessInput.industry} onValueChange={(value) => handleInputChange('industry', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select your industry" />
            </SelectTrigger>
            <SelectContent>
              {industries.map(industry => (
                <SelectItem key={industry} value={industry}>{industry}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="business_description">Business Description *</Label>
        <Textarea
          id="business_description"
          placeholder="Describe your business, what you do, and what makes you unique..."
          value={businessInput.business_description}
          onChange={(e) => handleInputChange('business_description', e.target.value)}
          className="min-h-[100px]"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="target_audience">Target Audience *</Label>
        <Textarea
          id="target_audience"
          placeholder="Describe your ideal customers (age, interests, demographics, etc.)"
          value={businessInput.target_audience}
          onChange={(e) => handleInputChange('target_audience', e.target.value)}
          className="min-h-[80px]"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="business_values">Business Values</Label>
        <Input
          id="business_values"
          placeholder="Enter values separated by commas (e.g., sustainability, innovation, quality)"
          value={businessInput.business_values.join(', ')}
          onChange={(e) => handleValuesChange(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label htmlFor="preferred_style">Preferred Style</Label>
          <Select value={businessInput.preferred_style} onValueChange={(value) => handleInputChange('preferred_style', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {styleOptions.map(style => (
                <SelectItem key={style} value={style}>{style}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="preferred_colors">Color Preference</Label>
          <Select value={businessInput.preferred_colors} onValueChange={(value) => handleInputChange('preferred_colors', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {colorOptions.map(color => (
                <SelectItem key={color} value={color}>{color}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <Button 
          onClick={createProject}
          disabled={!businessInput.business_name || !businessInput.business_description || !businessInput.industry || !businessInput.target_audience || isGenerating}
          className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating Project...
            </>
          ) : (
            <>
              <Zap className="mr-2 h-4 w-4" />
              Generate Brand Strategy
            </>
          )}
        </Button>
      </div>
    </div>
  );

  const BrandStrategyView = () => (
    <div className="space-y-6">
      {!brandStrategy ? (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <Lightbulb className="mx-auto h-12 w-12 text-violet-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Ready to Generate Your Brand Strategy</h3>
            <p className="text-gray-600 mb-6">
              Our AI will analyze your business and create a comprehensive brand strategy with personality, visual direction, and messaging framework.
            </p>
            <Button 
              onClick={generateBrandStrategy}
              disabled={isGenerating}
              className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing Your Business...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Brand Strategy
                </>
              )}
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-violet-600" />
                Brand Personality
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Primary Traits</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {brandStrategy.brand_personality.primary_traits?.map((trait, index) => (
                    <Badge key={index} variant="secondary">{trait}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <Label className="text-sm font-medium">Brand Archetype</Label>
                <p className="text-sm text-gray-600 mt-1">{brandStrategy.brand_personality.brand_archetype}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Brand Essence</Label>
                <p className="text-sm text-gray-600 mt-1">{brandStrategy.brand_personality.brand_essence}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-violet-600" />
                Visual Direction
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Design Style</Label>
                <p className="text-sm text-gray-600 mt-1">{brandStrategy.visual_direction.design_style}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Visual Mood</Label>
                <p className="text-sm text-gray-600 mt-1">{brandStrategy.visual_direction.visual_mood}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Color Palette</Label>
                <div className="flex gap-2 mt-2">
                  {brandStrategy.color_palette?.map((color, index) => (
                    <div
                      key={index}
                      className="w-8 h-8 rounded-full border-2 border-white shadow-md"
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Messaging Framework</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Tagline</Label>
                  <p className="text-sm text-gray-600 mt-1 italic">"{brandStrategy.messaging_framework.tagline}"</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Brand Promise</Label>
                  <p className="text-sm text-gray-600 mt-1">{brandStrategy.messaging_framework.brand_promise}</p>
                </div>
              </div>
              <div>
                <Label className="text-sm font-medium">Unique Value Proposition</Label>
                <p className="text-sm text-gray-600 mt-1">{brandStrategy.messaging_framework.unique_value_proposition}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {brandStrategy && (
        <div className="flex justify-end pt-4">
          <Button 
            onClick={() => {
              setActiveTab('visual-assets');
              setCurrentStep(2);
            }}
            className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
          >
            <Palette className="mr-2 h-4 w-4" />
            Generate Visual Assets
          </Button>
        </div>
      )}
    </div>
  );

  const VisualAssetsView = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { type: 'logo', label: 'Logo', context: 'Primary brand logo' },
          { type: 'business_card', label: 'Business Card', context: 'Professional business card design' },
          { type: 'letterhead', label: 'Letterhead', context: 'Company letterhead template' },
          { type: 'social_media_post', label: 'Social Media', context: 'Instagram post template' },
          { type: 'flyer', label: 'Flyer', context: 'Marketing flyer design' },
          { type: 'banner', label: 'Web Banner', context: 'Website banner design' }
        ].map(asset => (
          <Button
            key={asset.type}
            onClick={() => generateSingleAsset(asset.type, asset.context)}
            disabled={isGenerating}
            variant="outline"
            className="h-auto py-4 flex flex-col items-center gap-2"
          >
            <Palette className="h-6 w-6" />
            <span className="text-xs">{asset.label}</span>
          </Button>
        ))}
      </div>

      {generatedAssets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {generatedAssets.map((asset, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-sm capitalize">{asset.asset_type.replace('_', ' ')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="aspect-square bg-gray-100 rounded-lg mb-4 overflow-hidden">
                  <img 
                    src={asset.asset_url} 
                    alt={asset.asset_type}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => downloadAsset(asset)}
                    className="flex-1"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="flex justify-center pt-4">
        <Button 
          onClick={generateCompletePackage}
          disabled={isGenerating || !brandStrategy}
          size="lg"
          className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Generating Complete Package...
            </>
          ) : (
            <>
              <Rocket className="mr-2 h-5 w-5" />
              Generate Complete Brand Package
            </>
          )}
        </Button>
      </div>
    </div>
  );

  const CompletePackageView = () => (
    <div className="space-y-6">
      <div className="text-center py-8">
        <div className="max-w-2xl mx-auto">
          <Rocket className="mx-auto h-16 w-16 text-violet-600 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Your Brand Package is Ready!</h2>
          <p className="text-gray-600 mb-6">
            Complete professional brand identity generated in minutes. Download all assets and start building your brand presence.
          </p>
          <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{generatedAssets.length} Assets Generated</Badge>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Professional Quality</Badge>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Ready to Use</Badge>
            </div>
          </div>
        </div>
      </div>

      {generatedAssets.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {generatedAssets.map((asset, index) => (
            <Card key={index} className="overflow-hidden">
              <div className="aspect-square bg-gray-100">
                <img 
                  src={asset.asset_url} 
                  alt={asset.asset_type}
                  className="w-full h-full object-cover"
                />
              </div>
              <CardContent className="p-4">
                <h3 className="font-semibold capitalize mb-2">{asset.asset_type.replace('_', ' ')}</h3>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => downloadAsset(asset)}
                    className="flex-1 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="text-center pt-8">
        <Button 
          onClick={() => window.location.reload()}
          size="lg"
          variant="outline"
        >
          Create Another Brand
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-lg">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                  BrandForge AI
                </h1>
                <p className="text-sm text-gray-600">Transform Ideas into Complete Brands</p>
              </div>
            </div>
            {progress > 0 && (
              <div className="flex items-center gap-3">
                <Progress value={progress} className="w-32" />
                <span className="text-sm text-gray-600">{progress}%</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-center gap-4 mb-6">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === currentStep;
              const isCompleted = index < currentStep;
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`
                    flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all
                    ${isActive ? 'border-violet-600 bg-violet-600 text-white' : 
                      isCompleted ? 'border-green-500 bg-green-500 text-white' : 
                      'border-gray-300 bg-white text-gray-400'}
                  `}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="ml-3 hidden sm:block">
                    <p className={`text-sm font-medium ${isActive ? 'text-violet-600' : isCompleted ? 'text-green-600' : 'text-gray-500'}`}>
                      {step.title}
                    </p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`w-12 h-0.5 mx-4 ${isCompleted ? 'bg-green-500' : 'bg-gray-300'}`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="business-info">Business Info</TabsTrigger>
            <TabsTrigger value="brand-strategy" disabled={!currentProject}>Brand Strategy</TabsTrigger>
            <TabsTrigger value="visual-assets" disabled={!brandStrategy}>Visual Assets</TabsTrigger>
            <TabsTrigger value="complete-package" disabled={generatedAssets.length === 0}>Complete Package</TabsTrigger>
          </TabsList>

          <div className="mt-8">
            <TabsContent value="business-info">
              <Card>
                <CardHeader>
                  <CardTitle>Tell Us About Your Business</CardTitle>
                  <CardDescription>
                    Provide details about your business to generate a personalized brand strategy
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <BusinessInfoForm />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="brand-strategy">
              <Card>
                <CardHeader>
                  <CardTitle>AI-Generated Brand Strategy</CardTitle>
                  <CardDescription>
                    Comprehensive brand analysis with personality, visual direction, and messaging
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <BrandStrategyView />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="visual-assets">
              <Card>
                <CardHeader>
                  <CardTitle>Generate Visual Assets</CardTitle>
                  <CardDescription>
                    Create professional brand assets individually or generate a complete package
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <VisualAssetsView />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="complete-package">
              <Card>
                <CardHeader>
                  <CardTitle>Your Complete Brand Package</CardTitle>
                  <CardDescription>
                    Professional brand assets ready for download and use
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <CompletePackageView />
                </CardContent>
              </Card>
            </TabsContent>
          </div>
        </Tabs>
      </main>
    </div>
  );
}

export default App;
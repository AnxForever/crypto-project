"use client"

import { Input } from "@/components/ui/input"

import { useState, type ChangeEvent } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useToast } from "@/hooks/use-toast"
import { Database, Key, Lock, RefreshCw, ShieldCheck, FileText, Eye, EyeOff, ListFilter, Upload } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface MinsaPayTransaction {
  id: string
  timestamp: string
  merchantId: string
  userId: string
  transactionAmount: string // Keep as string to handle currency symbols if any
  currency: string
  paymentMethod: string
  location: string
  status: string
  [key: string]: string // For dynamic access
}

interface SM2KeyPair {
  publicKey: string
  privateKey: string
}

// Mock SM2 Crypto API (Simulating backend or WebAssembly module)
const MockSM2API = {
  generateKeyPair: async (): Promise<SM2KeyPair> => {
    await new Promise((resolve) => setTimeout(resolve, 500))
    return {
      publicKey: `SM2-PUB-${Math.random().toString(36).substring(2, 15)}`,
      privateKey: `SM2-PRIV-${Math.random().toString(36).substring(2, 15)}`,
    }
  },
  encrypt: async (data: string, publicKey: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 100)) // Faster for batch
    // In a real SM2, this would be complex elliptic curve math.
    // Output is typically a C1C3C2 structure, often hex or base64 encoded.
    return `SM2ENC(${btoa(data).substring(0, 20)}...)${publicKey.slice(-4)}`
  },
  decrypt: async (encryptedData: string, privateKey: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 100))
    if (!encryptedData.startsWith("SM2ENC(")) return "DECRYPTION_ERROR"
    try {
      // This is a highly simplified mock decryption
      const base64Part = encryptedData.substring(7, encryptedData.indexOf("...)"))
      return atob(base64Part)
    } catch (e) {
      return "DECRYPTION_ERROR_FORMAT"
    }
  },
}

const initialCsvData = `id,timestamp,merchantId,userId,transactionAmount,currency,paymentMethod,location,status
TXN001,2024-07-27T10:30:00Z,MERCH5001,USER101,150.75,CNY,WeChatPay,Shanghai,Completed
TXN002,2024-07-27T10:32:15Z,MERCH5002,USER102,88.00,CNY,Alipay,Beijing,Completed
TXN003,2024-07-27T10:35:40Z,MERCH5001,USER103,230.50,CNY,Card,Shanghai,Pending
TXN004,2024-07-27T10:38:05Z,MERCH5003,USER101,45.90,CNY,Alipay,Guangzhou,Completed
TXN005,2024-07-27T10:40:22Z,MERCH5002,USER104,1200.00,CNY,WeChatPay,Beijing,Failed`

export default function PKEApplicationPage() {
  const [sm2Keys, setSm2Keys] = useState<SM2KeyPair | null>(null)
  const [rawDataInput, setRawDataInput] = useState<string>(initialCsvData)
  const [transactions, setTransactions] = useState<MinsaPayTransaction[]>([])
  const [encryptedTransactions, setEncryptedTransactions] = useState<MinsaPayTransaction[]>([])
  const [fieldsToEncrypt, setFieldsToEncrypt] = useState<Record<keyof MinsaPayTransaction, boolean>>({
    id: false,
    timestamp: false,
    merchantId: false,
    userId: true, // Default to encrypt User ID
    transactionAmount: true, // Default to encrypt Amount
    currency: false,
    paymentMethod: false,
    location: true, // Default to encrypt Location
    status: false,
  })
  const [isProcessing, setIsProcessing] = useState(false)
  const [showDecrypted, setShowDecrypted] = useState(false)

  const { toast } = useToast()

  const availableFields = Object.keys(initialFieldsToEncryptState()) as Array<keyof MinsaPayTransaction>

  function initialFieldsToEncryptState(): Record<keyof MinsaPayTransaction, boolean> {
    // Dynamically create this based on a sample or predefined structure if needed
    return {
      id: false,
      timestamp: false,
      merchantId: false,
      userId: true,
      transactionAmount: true,
      currency: false,
      paymentMethod: false,
      location: true,
      status: false,
    }
  }

  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setRawDataInput(e.target?.result as string)
        parseAndLoadData(e.target?.result as string)
      }
      reader.readAsText(file)
    }
  }

  const parseAndLoadData = (data: string) => {
    try {
      const lines = data.trim().split("\n")
      if (lines.length < 2) {
        toast({
          title: "Invalid Data",
          description: "CSV data needs a header and at least one row.",
          variant: "destructive",
        })
        return []
      }
      const header = lines[0].split(",").map((s) => s.trim()) as Array<keyof MinsaPayTransaction>
      const parsedData = lines.slice(1).map((line) => {
        const values = line.split(",").map((s) => s.trim())
        const entry: Partial<MinsaPayTransaction> = {}
        header.forEach((key, index) => {
          entry[key] = values[index]
        })
        return entry as MinsaPayTransaction
      })
      setTransactions(parsedData)
      setEncryptedTransactions([]) // Clear previous encryption
      setShowDecrypted(false)
      toast({ title: "Data Loaded", description: `${parsedData.length} transactions parsed.` })
      return parsedData
    } catch (error) {
      toast({ title: "Data Parsing Error", description: "Failed to parse CSV data.", variant: "destructive" })
      setTransactions([])
      setEncryptedTransactions([])
      return []
    }
  }

  const generateSM2Keys = async () => {
    setIsProcessing(true)
    try {
      const keys = await MockSM2API.generateKeyPair()
      setSm2Keys(keys)
      toast({ title: "SM2 Keys Generated", description: "Public and Private keys are ready." })
    } catch (error) {
      toast({ title: "Key Generation Failed", variant: "destructive" })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleFieldToggle = (field: keyof MinsaPayTransaction) => {
    setFieldsToEncrypt((prev) => ({ ...prev, [field]: !prev[field] }))
  }

  const encryptData = async () => {
    if (!sm2Keys || transactions.length === 0) {
      toast({
        title: "Prerequisites Missing",
        description: "Please generate SM2 keys and load data first.",
        variant: "destructive",
      })
      return
    }
    setIsProcessing(true)
    setShowDecrypted(false)
    const newEncryptedTransactions: MinsaPayTransaction[] = []
    for (const tx of transactions) {
      const encryptedTx = { ...tx }
      for (const key of Object.keys(tx) as Array<keyof MinsaPayTransaction>) {
        if (fieldsToEncrypt[key] && tx[key]) {
          encryptedTx[key] = await MockSM2API.encrypt(tx[key], sm2Keys.publicKey)
        }
      }
      newEncryptedTransactions.push(encryptedTx)
    }
    setEncryptedTransactions(newEncryptedTransactions)
    toast({ title: "Data Encrypted", description: "Selected fields have been encrypted using SM2." })
    setIsProcessing(false)
  }

  // Decryption is mostly for display toggle, actual decryption happens on demand if needed
  // For this demo, we'll just toggle visibility of original vs encrypted.
  // A full decrypt function would mirror encryptData.

  const displayedTransactions = showDecrypted
    ? transactions
    : encryptedTransactions.length > 0
      ? encryptedTransactions
      : transactions

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-emerald-500 to-lime-500 bg-opacity-20">
            <Database className="h-6 w-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">PKE真实数据应用：民生付SM2加密</h1>
            <p className="text-gray-400">PKE Real Data Application: MinsaPay SM2 Encryption</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          演示如何使用国密SM2算法对真实的（模拟）民生付交易数据中的敏感字段进行加密保护。
          此应用场景展示了PKE在金融数据安全中的实际价值。
        </p>
      </div>

      {/* Step 1: Load Data & Generate SM2 Keys */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <FileText className="h-5 w-5 text-blue-400" />
              <span>步骤 1: 加载交易数据</span>
            </CardTitle>
            <CardDescription className="text-gray-400">粘贴CSV格式的MinsaPay交易数据或上传文件。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Label htmlFor="data-input" className="text-gray-300">
              粘贴CSV数据:
            </Label>
            <Textarea
              id="data-input"
              value={rawDataInput}
              onChange={(e) => setRawDataInput(e.target.value)}
              rows={8}
              className="bg-white/5 font-mono text-xs"
              placeholder="id,timestamp,merchantId,userId,transactionAmount,currency,paymentMethod,location,status..."
            />
            <div className="flex gap-2">
              <Button onClick={() => parseAndLoadData(rawDataInput)} className="w-full" variant="outline">
                <ListFilter className="mr-2 h-4 w-4" /> 解析数据
              </Button>
              <Label htmlFor="csv-upload" className="w-full">
                <Button asChild className="w-full" variant="outline">
                  <span>
                    <Upload className="mr-2 h-4 w-4" /> 上传CSV文件
                  </span>
                </Button>
                <Input id="csv-upload" type="file" accept=".csv" className="sr-only" onChange={handleFileUpload} />
              </Label>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Key className="h-5 w-5 text-green-400" />
              <span>步骤 2: 生成SM2密钥对</span>
            </CardTitle>
            <CardDescription className="text-gray-400">为数据加密/解密生成SM2公钥和私钥。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={generateSM2Keys}
              disabled={isProcessing}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:opacity-90"
            >
              {isProcessing && sm2Keys === null ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Key className="mr-2 h-4 w-4" />
              )}
              生成SM2密钥对
            </Button>
            {sm2Keys && (
              <div className="space-y-2 pt-2 border-t border-white/10">
                <Label className="text-gray-300">SM2公钥:</Label>
                <Textarea value={sm2Keys.publicKey} readOnly className="h-16 bg-white/5 text-xs font-mono" />
                <Label className="text-gray-300">SM2私钥 (妥善保管):</Label>
                <Textarea value={sm2Keys.privateKey} readOnly className="h-16 bg-white/5 text-xs font-mono" />
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Step 2: Select Fields & Encrypt */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Lock className="h-5 w-5 text-red-400" />
            <span>步骤 3: 选择敏感字段并加密</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-gray-300 mb-2 block">选择要加密的字段:</Label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {availableFields.map((field) => (
                <div key={field} className="flex items-center space-x-2 p-2 rounded-md bg-white/5">
                  <Checkbox
                    id={`field-${field}`}
                    checked={fieldsToEncrypt[field]}
                    onCheckedChange={() => handleFieldToggle(field)}
                    className="border-gray-500 data-[state=checked]:bg-purple-500 data-[state=checked]:border-purple-500"
                  />
                  <Label htmlFor={`field-${field}`} className="text-sm text-gray-300 capitalize">
                    {field.replace(/([A-Z])/g, " $1")} {/* Add space before caps */}
                  </Label>
                </div>
              ))}
            </div>
          </div>
          <Button
            onClick={encryptData}
            disabled={isProcessing || !sm2Keys || transactions.length === 0}
            className="w-full bg-gradient-to-r from-red-500 to-pink-500 hover:opacity-90"
          >
            {isProcessing && encryptedTransactions.length === 0 ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Lock className="mr-2 h-4 w-4" />
            )}
            使用SM2加密选中字段
          </Button>
        </CardContent>
      </Card>

      {/* Step 3: View Data (Original/Encrypted/Decrypted) */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2 justify-between">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="h-5 w-5 text-teal-400" />
              <span>步骤 4: 查看处理后数据</span>
            </div>
            {encryptedTransactions.length > 0 && (
              <Button
                onClick={() => setShowDecrypted(!showDecrypted)}
                variant="outline"
                size="sm"
                className="text-white border-white/20 hover:bg-white/10"
              >
                {showDecrypted ? <EyeOff className="mr-2 h-4 w-4" /> : <Eye className="mr-2 h-4 w-4" />}
                {showDecrypted ? "查看加密数据" : "查看解密数据 (模拟)"}
              </Button>
            )}
          </CardTitle>
          <CardDescription className="text-gray-400">
            下方表格展示了处理后的MinsaPay交易数据。加密字段将以密文形式显示。
            {encryptedTransactions.length > 0 && " 使用上方按钮切换查看原始/解密数据。"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {transactions.length === 0 && (
            <div className="text-center py-10">
              <Database className="mx-auto h-12 w-12 text-gray-500" />
              <p className="mt-2 text-sm text-gray-400">请先加载并解析数据。</p>
            </div>
          )}
          {transactions.length > 0 && (
            <div className="overflow-x-auto rounded-lg border border-white/10 max-h-[500px]">
              <Table className="min-w-full">
                <TableHeader className="sticky top-0 bg-slate-800/80 backdrop-blur-sm">
                  <TableRow>
                    {availableFields.map((field) => (
                      <TableHead key={field} className="text-white px-3 py-2 text-xs capitalize">
                        {field.replace(/([A-Z])/g, " $1")}
                        {fieldsToEncrypt[field] && <Lock className="inline-block h-3 w-3 ml-1 text-red-400" />}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {displayedTransactions.map((tx, index) => (
                    <TableRow key={tx.id + index} className="hover:bg-white/5">
                      {availableFields.map((field) => (
                        <TableCell key={field} className="text-gray-300 px-3 py-2 text-xs font-mono whitespace-nowrap">
                          {tx[field]?.length > 30 &&
                          !showDecrypted &&
                          fieldsToEncrypt[field] &&
                          encryptedTransactions.length > 0
                            ? `${tx[field].substring(0, 15)}...`
                            : tx[field]}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Alert variant="default" className="glass-card border-teal-500/30">
        <ShieldCheck className="h-4 w-4" />
        <AlertTitle className="text-teal-300">关于SM2和数据保护</AlertTitle>
        <AlertDescription className="text-xs text-gray-400 space-y-1">
          <p>
            SM2是中国国家密码管理局发布的公钥密码算法，广泛应用于国内金融、政务等重要领域，提供高安全性的数据加密和数字签名功能。
          </p>
          <p>
            对此类交易数据中的敏感字段（如用户ID、交易金额、位置信息）进行加密，是保护用户隐私、符合数据安全法规（如《个人信息保护法》）的重要措施。
          </p>
        </AlertDescription>
      </Alert>
    </div>
  )
}

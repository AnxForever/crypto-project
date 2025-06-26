"use client"

import { Input } from "@/components/ui/input"

import { useState, type ChangeEvent } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useToast } from "@/hooks/use-toast"
import {
  ShieldIcon as ShieldUser,
  KeyRound,
  LockKeyhole,
  RefreshCw,
  ShieldCheck,
  FileText,
  Eye,
  EyeOff,
  ListFilter,
  Upload,
  Settings,
  UserCog,
  Hospital,
} from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface HealthRecord {
  Name: string
  Age: string
  Gender: string
  "Blood Type": string
  "Medical Condition": string
  "Date of Admission": string
  Doctor: string
  Hospital: string
  "Insurance Provider": string
  "Billing Amount": string
  "Room Number": string
  "Admission Type": string
  "Discharge Date": string
  Medication: string
  "Test Results": string
  [key: string]: string // For dynamic access
}

interface IBESystemParams {
  scheme: "Sakai-Kasahara"
  masterPublicKey: string
  masterSecretKey: string // Kept by PKG, not usually exposed client-side
}

interface UserIBEPrivateKey {
  identity: string
  privateKey: string
}

// Mock Sakai-Kasahara IBE API
const MockSakaiKasaharaAPI = {
  setup: async (): Promise<IBESystemParams> => {
    await new Promise((resolve) => setTimeout(resolve, 700))
    return {
      scheme: "Sakai-Kasahara",
      masterPublicKey: `SK-MPK-${Math.random().toString(36).substring(2, 15)}`,
      masterSecretKey: `SK-MSK-${Math.random().toString(36).substring(2, 15)}`, // For simulation
    }
  },
  extractPrivateKey: async (identity: string, masterSecretKey: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 300))
    // In real SK-IBE, this involves complex elliptic curve operations with MSK.
    return `SK-USERKEY(${identity})-${masterSecretKey.slice(-4)}-${Math.random().toString(36).substring(2, 10)}`
  },
  encrypt: async (data: string, identity: string, masterPublicKey: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 150))
    // Real SK-IBE encryption involves hashing identity to a curve point, pairings, etc.
    return `SK-ENC(${btoa(data).substring(0, 15)}...ID:${identity.substring(0, 5)})${masterPublicKey.slice(-4)}`
  },
  decrypt: async (encryptedData: string, userPrivateKey: string, identity: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 150))
    if (!encryptedData.startsWith("SK-ENC(") || !userPrivateKey.includes(`SK-USERKEY(${identity})`)) {
      return "DECRYPTION_ERROR_KEY_MISMATCH"
    }
    try {
      const base64Part = encryptedData.substring(7, encryptedData.indexOf("...ID:"))
      return atob(base64Part)
    } catch (e) {
      return "DECRYPTION_ERROR_FORMAT"
    }
  },
}

const initialCsvHealthData = `Name,Age,Gender,Blood Type,Medical Condition,Date of Admission,Doctor,Hospital,Insurance Provider,Billing Amount,Room Number,Admission Type,Discharge Date,Medication,Test Results
Bobby JacksOn,30,Male,B-,Cancer,2024-01-31,Matthew Smith,Sons and Miller,Blue Cross,18856.28,328,Urgent,2024-02-02,Paracetamol,Normal
LesLie TErRy,62,Male,A+,Obesity,2019-08-20,Samantha Davies,Kim Inc,Medicare,33643.33,265,Emergency,2019-08-26,Ibuprofen,Inconclusive
DaNnY sMitH,76,Female,A-,Obesity,2022-09-22,Tiffany Mitchell,Cook PLC,Aetna,27955.10,205,Emergency,2022-10-07,Aspirin,Normal
andrEw waTtS,28,Female,O+,Diabetes,2020-11-18,Kevin Wells,"Hernandez Rogers and Vang,",Medicare,37909.78,450,Elective,2020-12-18,Ibuprofen,Abnormal
adrIENNE bEll,43,Female,AB+,Cancer,2022-09-19,Kathleen Hanna,White-White,Aetna,14238.32,458,Urgent,2022-10-09,Penicillin,Abnormal
EMILY JOHNSOn,36,Male,A+,Asthma,2023-12-20,Taylor Newton,Nunez-Humphrey,UnitedHealthcare,48145.11,389,Urgent,2023-12-24,Ibuprofen,Normal
edwArD EDWaRDs,21,Female,AB-,Diabetes,2020-11-03,Kelly Olson,Group Middleton,Medicare,19580.87,389,Emergency,2020-11-15,Paracetamol,Inconclusive`

export default function IBEApplicationPage() {
  const [ibeParams, setIbeParams] = useState<IBESystemParams | null>(null)
  const [userKeys, setUserKeys] = useState<UserIBEPrivateKey[]>([])
  const [rawDataInput, setRawDataInput] = useState<string>(initialCsvHealthData)
  const [healthRecords, setHealthRecords] = useState<HealthRecord[]>([])
  const [encryptedHealthRecords, setEncryptedHealthRecords] = useState<HealthRecord[]>([])
  const [identityField, setIdentityField] = useState<keyof HealthRecord>("Name") // Field to use as identity
  const [decryptingIdentity, setDecryptingIdentity] = useState<string>("") // For whom to decrypt

  const initialFieldsToEncrypt: Record<string, boolean> = {
    Name: false, // Usually not encrypted if used as identity, but can be
    Age: true,
    Gender: false,
    "Blood Type": true,
    "Medical Condition": true,
    "Date of Admission": false,
    Doctor: false, // Could be an identity for decryption
    Hospital: false,
    "Insurance Provider": false,
    "Billing Amount": true,
    "Room Number": true,
    "Admission Type": false,
    "Discharge Date": false,
    Medication: true,
    "Test Results": true,
  }
  const [fieldsToEncrypt, setFieldsToEncrypt] = useState<Record<string, boolean>>(initialFieldsToEncrypt)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showDecrypted, setShowDecrypted] = useState(false)

  const { toast } = useToast()

  const availableFields = healthRecords.length > 0 ? (Object.keys(healthRecords[0]) as Array<keyof HealthRecord>) : []

  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        setRawDataInput(content)
        parseAndLoadData(content)
      }
      reader.readAsText(file)
    }
  }

  const parseAndLoadData = (data: string) => {
    try {
      const lines = data.trim().split("\n")
      if (lines.length < 2) throw new Error("CSV data needs a header and at least one data row.")
      const header = lines[0].split(",").map((s) => s.trim())
      const parsedData = lines.slice(1).map((line) => {
        const values = line.split(",").map((s) => s.trim())
        const entry: Partial<HealthRecord> = {}
        header.forEach((key, index) => {
          entry[key as keyof HealthRecord] = values[index]
        })
        return entry as HealthRecord
      })
      setHealthRecords(parsedData)
      setEncryptedHealthRecords([])
      setShowDecrypted(false)
      // Dynamically set fieldsToEncrypt based on loaded headers
      const newFieldsToEncrypt: Record<string, boolean> = {}
      header.forEach((h) => {
        newFieldsToEncrypt[h] = initialFieldsToEncrypt[h] !== undefined ? initialFieldsToEncrypt[h] : true // Default to encrypt new fields
      })
      setFieldsToEncrypt(newFieldsToEncrypt)

      toast({ title: "Data Loaded", description: `${parsedData.length} health records parsed.` })
    } catch (error: any) {
      toast({
        title: "Data Parsing Error",
        description: error.message || "Failed to parse CSV data.",
        variant: "destructive",
      })
      setHealthRecords([])
    }
  }

  const setupIBESystem = async () => {
    setIsProcessing(true)
    try {
      const params = await MockSakaiKasaharaAPI.setup()
      setIbeParams(params)
      setUserKeys([]) // Reset user keys
      toast({ title: "Sakai-Kasahara IBE System Setup", description: "PKG initialized, master keys generated." })
    } catch (error) {
      toast({ title: "IBE Setup Failed", variant: "destructive" })
    } finally {
      setIsProcessing(false)
    }
  }

  const extractUserKey = async (identity: string) => {
    if (!ibeParams) {
      toast({ title: "System Not Setup", description: "Please set up IBE system first.", variant: "destructive" })
      return
    }
    if (userKeys.find((k) => k.identity === identity)) {
      toast({ title: "Key Exists", description: `Private key for ${identity} already extracted.` })
      return
    }
    setIsProcessing(true)
    try {
      const privateKey = await MockSakaiKasaharaAPI.extractPrivateKey(identity, ibeParams.masterSecretKey)
      setUserKeys((prev) => [...prev, { identity, privateKey }])
      toast({ title: "User Private Key Extracted", description: `Key for identity '${identity}' ready.` })
    } catch (error) {
      toast({ title: "Key Extraction Failed", variant: "destructive" })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleFieldToggle = (field: string) => {
    setFieldsToEncrypt((prev) => ({ ...prev, [field]: !prev[field] }))
  }

  const encryptData = async () => {
    if (!ibeParams || healthRecords.length === 0) {
      toast({ title: "Prerequisites Missing", description: "Setup IBE system and load data.", variant: "destructive" })
      return
    }
    setIsProcessing(true)
    setShowDecrypted(false)
    const newEncryptedRecords: HealthRecord[] = []
    for (const record of healthRecords) {
      const encryptedRecord = { ...record }
      const recordIdentity = record[identityField]
      if (!recordIdentity) {
        toast({
          title: "Missing Identity",
          description: `Record missing value for identity field '${identityField}'. Skipping.`,
          variant: "warning",
        })
        newEncryptedRecords.push(record) // Push original if identity is missing
        continue
      }
      for (const key of Object.keys(record) as Array<keyof HealthRecord>) {
        if (fieldsToEncrypt[key] && record[key]) {
          encryptedRecord[key] = await MockSakaiKasaharaAPI.encrypt(
            record[key],
            recordIdentity,
            ibeParams.masterPublicKey,
          )
        }
      }
      newEncryptedRecords.push(encryptedRecord)
    }
    setEncryptedHealthRecords(newEncryptedRecords)
    toast({ title: "Data Encrypted", description: "Selected fields encrypted using Sakai-Kasahara IBE." })
    setIsProcessing(false)
  }

  const decryptDataForDisplay = async () => {
    if (!decryptingIdentity) {
      toast({ title: "Select Identity", description: "Please choose an identity to decrypt for.", variant: "warning" })
      return
    }
    const userKeyEntry = userKeys.find((k) => k.identity === decryptingIdentity)
    if (!userKeyEntry) {
      toast({
        title: "Private Key Missing",
        description: `No private key extracted for identity '${decryptingIdentity}'. Extract key first.`,
        variant: "destructive",
      })
      return
    }
    if (encryptedHealthRecords.length === 0) {
      toast({
        title: "No Encrypted Data",
        description: "Encrypt data first before attempting decryption.",
        variant: "warning",
      })
      return
    }

    setIsProcessing(true)
    // For a simpler toggle: if showDecrypted is true, we show the original data.
    // The actual decryption logic would be more granular.
    setShowDecrypted(true)
    toast({ title: "Decryption View", description: `Displaying decrypted data for identity '${decryptingIdentity}'.` })
    setIsProcessing(false)
  }

  const displayedRecords =
    showDecrypted && decryptingIdentity
      ? healthRecords.map((hr) => {
          // A more accurate "showDecrypted" view
          const encryptedVersion = encryptedHealthRecords.find((er) => er.Name === hr.Name) // Assuming Name is unique
          if (hr[identityField] === decryptingIdentity && encryptedVersion) {
            const userKey = userKeys.find((uk) => uk.identity === decryptingIdentity)
            if (userKey) {
              // This is still a simplification. Real decryption would be async and per field.
              // For demo, we just show original if identity matches and key exists.
              return hr
            }
          }
          return encryptedVersion || hr // Fallback to encrypted or original if no match
        })
      : encryptedHealthRecords.length > 0
        ? encryptedHealthRecords
        : healthRecords

  const uniqueIdentitiesForDecryption = Array.from(
    new Set(healthRecords.map((hr) => hr[identityField]).filter(Boolean)),
  )

  return (
    <div className="space-y-6">
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 bg-opacity-20">
            <Hospital className="h-6 w-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">IBE真实数据应用：医疗记录Sakai-Kasahara加密</h1>
            <p className="text-gray-400">IBE Real Data: Secure Health Records with Sakai-Kasahara</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          演示使用Sakai-Kasahara IBE方案对（模拟）医疗记录中的敏感信息进行加密。
          展示如何基于患者或医生身份进行数据保护，简化医疗信息共享的密钥管理。
        </p>
      </div>

      {/* Step 1: Setup IBE System & Load Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Settings className="h-5 w-5 text-purple-400" />
              <span>步骤 1: 初始化Sakai-Kasahara IBE系统 (PKG)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              onClick={setupIBESystem}
              disabled={isProcessing}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500"
            >
              {isProcessing && !ibeParams ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Settings className="mr-2 h-4 w-4" />
              )}
              初始化PKG
            </Button>
            {ibeParams && (
              <div className="mt-3 p-3 bg-white/5 rounded-md text-xs font-mono">
                <p className="text-green-400">Sakai-Kasahara系统已初始化。</p>
                <p className="text-gray-300">主公钥: {ibeParams.masterPublicKey.substring(0, 30)}...</p>
                <p className="text-gray-500">(主私钥由PKG安全保管)</p>
              </div>
            )}
          </CardContent>
        </Card>
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <FileText className="h-5 w-5 text-blue-400" />
              <span>步骤 2: 加载医疗数据</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Label htmlFor="health-data-input" className="text-gray-300">
              粘贴CSV数据:
            </Label>
            <Textarea
              id="health-data-input"
              value={rawDataInput}
              onChange={(e) => setRawDataInput(e.target.value)}
              rows={5}
              className="bg-white/5 font-mono text-xs"
              placeholder="Name,Age,Gender,Blood Type,Medical Condition..."
            />
            <div className="flex gap-2">
              <Button onClick={() => parseAndLoadData(rawDataInput)} className="w-full" variant="outline">
                <ListFilter className="mr-2 h-4 w-4" /> 解析数据
              </Button>
              <Label htmlFor="csv-health-upload" className="w-full">
                <Button asChild className="w-full" variant="outline">
                  <span>
                    <Upload className="mr-2 h-4 w-4" /> 上传CSV文件
                  </span>
                </Button>
                <Input
                  id="csv-health-upload"
                  type="file"
                  accept=".csv"
                  className="sr-only"
                  onChange={handleFileUpload}
                />
              </Label>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Step 3: Extract User Keys & Select Fields */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <UserCog className="h-5 w-5 text-green-400" />
            <span>步骤 3: 提取用户私钥 (PKG操作) 和选择加密字段</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-gray-300 mb-1 block">选择身份字段 (用于加密/解密目标):</Label>
            <select
              value={identityField}
              onChange={(e) => setIdentityField(e.target.value as keyof HealthRecord)}
              className="w-full p-2 rounded-md bg-white/10 border border-white/20 text-white"
              disabled={healthRecords.length === 0}
            >
              {availableFields.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">选定此字段的值作为IBE加密/解密的身份标识。</p>
          </div>
          <div>
            <Label className="text-gray-300 mb-2 block">为需要解密的用户/医生提取私钥:</Label>
            {/* Simplified: allow extracting for any unique identity present in the chosen identityField */}
            {uniqueIdentitiesForDecryption.slice(0, 5).map(
              (
                id, // Show first 5 unique identities as example
              ) => (
                <Button
                  key={id}
                  variant="outline"
                  size="sm"
                  onClick={() => extractUserKey(id)}
                  disabled={isProcessing || !ibeParams || userKeys.some((k) => k.identity === id)}
                  className="mr-2 mb-2 text-xs border-white/20 hover:bg-white/10"
                >
                  {userKeys.some((k) => k.identity === id) ? (
                    <ShieldCheck className="mr-1 h-3 w-3 text-green-400" />
                  ) : (
                    <KeyRound className="mr-1 h-3 w-3" />
                  )}
                  提取密钥: {id}
                </Button>
              ),
            )}
            {userKeys.length > 0 && (
              <div className="mt-2 space-y-1 text-xs">
                {userKeys.map((uk) => (
                  <p key={uk.identity} className="text-green-400">
                    密钥已提取: {uk.identity} ({uk.privateKey.substring(0, 20)}...)
                  </p>
                ))}
              </div>
            )}
          </div>
          <div>
            <Label className="text-gray-300 mb-2 block">选择要加密的字段:</Label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {availableFields.map((field) => (
                <div key={field} className="flex items-center space-x-2 p-2 rounded-md bg-white/5">
                  <Checkbox
                    id={`health-field-${field}`}
                    checked={!!fieldsToEncrypt[field]}
                    onCheckedChange={() => handleFieldToggle(field)}
                    className="border-gray-500 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500"
                  />
                  <Label htmlFor={`health-field-${field}`} className="text-sm text-gray-300 capitalize">
                    {field}
                  </Label>
                </div>
              ))}
            </div>
          </div>
          <Button
            onClick={encryptData}
            disabled={isProcessing || !ibeParams || healthRecords.length === 0}
            className="w-full bg-gradient-to-r from-red-500 to-pink-500 hover:opacity-90"
          >
            {isProcessing && encryptedHealthRecords.length === 0 ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <LockKeyhole className="mr-2 h-4 w-4" />
            )}
            使用IBE加密选中字段
          </Button>
        </CardContent>
      </Card>

      {/* Step 4: View Data */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2 justify-between">
            <div className="flex items-center space-x-2">
              <ShieldUser className="h-5 w-5 text-teal-400" />
              <span>步骤 4: 查看处理后医疗数据</span>
            </div>
            {encryptedHealthRecords.length > 0 && (
              <div className="flex items-center gap-2">
                <select
                  value={decryptingIdentity}
                  onChange={(e) => setDecryptingIdentity(e.target.value)}
                  className="p-1.5 rounded-md bg-white/10 border border-white/20 text-white text-xs"
                  disabled={userKeys.length === 0}
                >
                  <option value="">选择解密身份...</option>
                  {userKeys.map((uk) => (
                    <option key={uk.identity} value={uk.identity}>
                      {uk.identity}
                    </option>
                  ))}
                </select>
                <Button
                  onClick={decryptDataForDisplay}
                  variant="outline"
                  size="sm"
                  className="text-white border-white/20 hover:bg-white/10"
                  disabled={!decryptingIdentity || isProcessing}
                >
                  {showDecrypted && decryptingIdentity ? (
                    <EyeOff className="mr-2 h-4 w-4" />
                  ) : (
                    <Eye className="mr-2 h-4 w-4" />
                  )}
                  {showDecrypted && decryptingIdentity ? "查看加密" : "查看解密"}
                </Button>
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {healthRecords.length === 0 && <div className="text-center py-10 text-gray-400">请先加载并解析数据。</div>}
          {healthRecords.length > 0 && (
            <div className="overflow-x-auto rounded-lg border border-white/10 max-h-[500px]">
              <Table className="min-w-full">
                <TableHeader className="sticky top-0 bg-slate-800/80 backdrop-blur-sm">
                  <TableRow>
                    {availableFields.map((field) => (
                      <TableHead key={field} className="text-white px-3 py-2 text-xs capitalize">
                        {field}
                        {fieldsToEncrypt[field] && <LockKeyhole className="inline-block h-3 w-3 ml-1 text-red-400" />}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {displayedRecords.map((record, index) => (
                    <TableRow key={index} className="hover:bg-white/5">
                      {availableFields.map((field) => (
                        <TableCell key={field} className="text-gray-300 px-3 py-2 text-xs font-mono whitespace-nowrap">
                          {record[field]?.length > 25 &&
                          fieldsToEncrypt[field] &&
                          encryptedHealthRecords.length > 0 &&
                          (!showDecrypted || record[identityField] !== decryptingIdentity)
                            ? `${record[field].substring(0, 12)}...`
                            : record[field]}
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

      <Alert variant="default" className="glass-card border-cyan-500/30">
        <ShieldCheck className="h-4 w-4" />
        <AlertTitle className="text-cyan-300">IBE在医疗数据保护中的应用</AlertTitle>
        <AlertDescription className="text-xs text-gray-400 space-y-1">
          <p>
            Sakai-Kasahara等IBE方案允许使用易于管理的身份（如患者ID、医生邮箱）作为公钥。这极大地简化了传统PKI中复杂的证书管理。
          </p>
          <p>
            在医疗场景中，可以为特定医生或部门加密患者记录，只有持有对应身份私钥的授权人员才能解密，从而实现精细化的访问控制和数据安全共享。
            例如，可以将患者 "Bobby Jackson" 的记录用其主治医生 "Matthew Smith" 的身份进行加密，确保只有 Dr. Smith
            能访问。
          </p>
        </AlertDescription>
      </Alert>
    </div>
  )
}

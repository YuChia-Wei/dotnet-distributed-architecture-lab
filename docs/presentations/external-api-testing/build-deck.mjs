import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const skill=process.env.SKILL_DIR;
const python=process.env.RUNTIME_PYTHON;
if(!path.isAbsolute(skill??'')||!path.isAbsolute(python??''))throw new Error('Set absolute SKILL_DIR and RUNTIME_PYTHON');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#F8FAFB',navy:'#172033',teal:'#176B57',ink:'#273346',muted:'#536476',rule:'#CAD5DA',pale:'#EAF3EF',white:'#FFFFFF'};
const font='Microsoft JhengHei';
function shp(s,g,x,y,w,h,fill='none',edge='none',width=0){return s.shapes.add({geometry:g,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:edge,width}})}
function T(s,t,x,y,w,h,size=28,bold=false,color=C.ink,alignment='left'){const q=shp(s,'textbox',x,y,w,h);q.text=t;q.text.style={typeface:font,fontSize:size,bold,color,alignment,verticalAlignment:'middle',wrap:'square',autoFit:'none'};return q}
function L(s,x,y,w,color=C.rule,width=2){return shp(s,'line',x,y,w,0,'none',color,width)}
function B(s,t,x,y,w,h,fill=C.white,size=23){const q=shp(s,'rect',x,y,w,h,fill,C.teal,1.5);q.text=t;q.text.style={typeface:font,fontSize:size,bold:true,color:C.navy,alignment:'center',verticalAlignment:'middle',wrap:'square',autoFit:'none'};return q}
function slide(title,notes){const s=P.slides.add();s.background.fill=C.bg;T(s,title,72,39,1135,80,43,true,C.navy);L(s,72,135,1136,C.teal,4);s.speakerNotes.textFrame.setText(notes);return s}
function rows(s,data,y=172,gap=104){data.forEach(([a,b],i)=>{const yy=y+i*gap;T(s,a,74,yy,297,80,27,true,C.teal);T(s,b,390,yy,806,83,27,false,C.ink);L(s,74,yy+86,1132,C.rule,1)})}
function bullets(s,data,y=174,gap=105){data.forEach((v,i)=>{const yy=y+i*gap;T(s,'•',75,yy,45,77,32,true,C.teal);T(s,v,112,yy,1082,82,29)})}
const src=(...x)=>`講者提示：以此頁的關係或狀態為主線口述。所有執行結果以當次讀回為準。\n來源：\n${x.map(y=>'- '+y).join('\n')}`;
const proc='.dev/operations/procurement-supplier-lab.md',front='.dev/operations/commerce-frontend.md';
const arch='.dev/workflows/2026-09-26-procurement-supplier-lab/architecture.md',spec='.dev/workflows/2026-09-26-procurement-supplier-lab/specifications.md';

{const s=P.slides.add();s.background.fill=C.bg;T(s,'外部 API 測試實驗',73,177,1130,111,62,true,C.navy);T(s,'WireMock.Net、Microcks 與採購收貨流程',75,301,1110,90,36,true,C.teal);T(s,'團隊導覽 · 約 20 分鐘',76,529,650,50,26,false,C.muted);s.speakerNotes.textFrame.setText('開場：以已實作的 localhost 實驗為例。先看入口與路由，再演示 mock、proxy、hybrid、逾時協調及真正收貨。\n來源：'+proc+'；'+front)}

{const s=slide('今天要回答的四件事',src(proc));rows(s,[['服務在哪裡','前台、管理後台、採購 API 與兩套測試引擎'],['模式怎麼選','mock、proxy、hybrid 的行為與證據'],['失敗怎麼處理','提交後逾時，沿原供應商查證'],['庫存何時變動','登錄實際收貨後，由事件進 Inventory']])}

{const s=slide('測試引擎與業務轉接器',src(arch,spec));T(s,'測試引擎',74,185,480,60,36,true,C.teal);T(s,'回應供應商 HTTP 契約\n保留原生 mapping、dispatch 與 request 證據',74,260,488,180,29);T(s,'業務轉接器',695,185,490,60,36,true,C.teal);T(s,'ISupplierGateway 由 Procurement 使用\n核對身分、狀態與價格，記錄採購結果',695,260,505,180,29);shp(s,'line',630,185,0,325,'none',C.rule,2);T(s,'測試路由不決定採購單與庫存的業務規則。',74,544,1110,72,31,true,C.navy)}

{const s=slide('本機服務拓撲',src(front,proc));const a=B(s,'瀏覽器\n/web/  /admin/',73,200,211,106,C.pale),b=B(s,'YARP\n127.0.0.1:8888',341,200,246,106),c=B(s,'Procurement API',683,192,252,88),d=B(s,'管理控制 API',683,340,252,88),e=B(s,'供應商路由\ndirect / wiremock / microcks',989,185,219,125,C.pale,20),f=B(s,'Sandbox 與\n原生測試引擎',989,342,219,102);for(const [u,v] of [[a,b],[b,c],[b,d],[c,e],[d,f]])s.shapes.connect(u,v,{fromSide:'right',toSide:'left',line:{style:'solid',fill:C.teal,width:2}});T(s,'/api/products、/api/orders、/api/inventory 也由 YARP 提供同源入口。',75,540,1100,70,25,false,C.muted)}

{const s=slide('操作入口與原生入口',src(front,proc));rows(s,[['作業前台','http://127.0.0.1:8888/web/'],['管理後台','http://127.0.0.1:8888/admin/'],['WireMock 控制','/api/admin/supplier-mock/control/*'],['Microcks UI','http://127.0.0.1:8184/']],167,96);T(s,'目前是 localhost 實驗入口，沒有新增登入或角色授權。',74,579,1105,60,25,false,C.muted)}

{const s=slide('WireMock.Net 的三種模式',src(arch,proc,'https://wiremock.org/dotnet/proxying/','https://wiremock.org/dotnet/admin-api-reference/'));rows(s,[['mock','支援路由使用本機範例，不打 Sandbox'],['proxy','原生 proxy 將請求送往固定 Sandbox 上游'],['hybrid','符合固定範例走 priority 1；其餘走 priority 10 proxy']],183,111);T(s,'控制頁由本 repository 的 SupplierMock.WebApi 提供，並顯示 mapping 與 request journal。',74,550,1115,95,27,true,C.navy)}

{const s=slide('Microcks 的派送邊界',src(arch,front,'https://microcks.io/documentation/explanations/dispatching/','https://microcks.io/blog/new-proxy-features-1.9.1/'));bullets(s,['匯入 Supplier API 1.0.0 的 OpenAPI 範例與 dispatcher','mock、proxy、hybrid 使用各自的受控 YAML','PROXY_FALLBACK 處理已匯入 operation 的回應比對'],181,108);T(s,'未知路徑不保證全域透傳；切換後仍要讀回原生狀態與請求來源。',74,537,1120,91,29,true,C.navy)}

{const s=slide('報價查詢的模式與觀察點',src(proc,spec));T(s,'模式',74,178,205,55,28,true,C.teal);T(s,'回應來源',347,178,375,55,28,true,C.teal);T(s,'Sandbox request log',836,178,355,55,28,true,C.teal);L(s,74,236,1132,C.rule,2);[['mock','origin=wiremock / microcks','沒有新增上游請求'],['proxy','origin=sandbox','對應 request 增加'],['hybrid','MOCK-001：範例\nREAL-001：Sandbox','依 SKU 分流']].forEach((r,i)=>{const y=251+i*113;T(s,r[0],74,y,205,92,30,true,C.navy);T(s,r[1],347,y,437,92,26);T(s,r[2],836,y,356,92,26);L(s,74,y+100,1132,C.rule,1)});T(s,'GET 報價無 clientRequestId；隔離操作並核對 SKU、origin 與 Sandbox 請求。',74,616,1110,55,23,false,C.muted)}

{const s=slide('固定範例需要完整身分',src(spec,proc));bullets(s,['供應商 POST 含 clientRequestId、SKU、數量、價格與幣別','固定 MOCK-001 範例只回應文件化的識別與內容','欄位改動或巢狀誘餌不能冒用固定範例'],181,106);T(s,'等值價格 100 與 100.00 可匹配；Sandbox 同 key 不同 payload 應衝突。',74,540,1100,94,29,true,C.navy)}

{const s=slide('一次供應商請求的路徑',src(arch,proc));const x=[77,357,637,917],names=['操作員','Procurement','Mock 引擎','Sandbox'];x.forEach((v,i)=>{B(s,names[i],v,190,214,64,C.pale,23);shp(s,'line',v+107,255,0,349,'none',C.rule,1.5)});const anchor=(i,y)=>shp(s,'ellipse',x[i]+106,y-1,2,2);[[0,1,306,'選 provider 與 SKU'],[1,2,361,'送供應商 HTTP'],[2,3,416,'需要透傳時送上游'],[3,2,471,'回應 origin=sandbox'],[2,1,526,'回傳供應商回應'],[1,0,581,'回傳採購結果']].forEach(([a,b,y,t])=>{s.shapes.connect(anchor(a,y),anchor(b,y),{kind:'straight',fromSide:a<b?'right':'left',toSide:a<b?'left':'right',line:{style:'solid',fill:C.teal,width:2.5},tail:{type:'triangle',width:'sm',length:'sm'}});T(s,t,Math.min(x[a],x[b])+107,y-49,Math.abs(x[b]-x[a]),35,20,true,C.navy,'center')});T(s,'request journal 另由控制 API 查詢；Microcks hybrid 回退限已匯入 operation。',74,625,1110,52,23,false,C.muted)}

{const s=slide('提交後逾時的協調',src(arch,spec,proc));rows(s,[['先保存識別','Procurement 先持久化 clientRequestId'],['供應商可能已提交','Sandbox 可在寫入後延遲，呼叫端逾時'],['以原識別查詢','reconcile 對原 provider 執行 GET'],['結果仍未知','保留 SubmissionUnknown；用同 key 明確重試']],169,101);T(s,'逾時不能證明失敗，也不能觸發新的採購識別。',74,604,1110,58,29,true,C.navy)}

{const s=slide('真正入庫的事件路徑',src(arch,spec));const names=['Accepted\n採購單','登錄\nReceiptId','Procurement outbox\nWolverine 持久交接','Kafka','Inventory\n收貨去重'];const xs=[58,299,540,781,1022];names.forEach((v,i)=>{B(s,v,xs[i],242,199,103,i===4?C.pale:C.white,i===2?18:21);if(i)shp(s,'line',xs[i-1]+199,293,42,0,'none',C.teal,3)});T(s,'接受採購單時，庫存維持原值。',72,404,1135,71,33,true,C.navy);T(s,'實際收貨後，同一 ReceiptId 重播只返回原結果。',72,495,1135,71,30);T(s,'outbox 的 published_at 僅代表持久交接；Inventory 用 ReceiptId 保護單次庫存效果。',72,578,1135,80,24,false,C.muted)}

{const s=slide('示範一：確認 mock 與 proxy',src(proc,front));rows(s,[['準備','開 /admin/ 整合工具，記下 request journal 基線'],['mock','查 MOCK-001；看 mock origin、Sandbox 不增加'],['proxy','查 REAL-001；看 sandbox origin、上游請求增加'],['hybrid','兩個 SKU 各查一次，對照兩種來源']],171,105);T(s,'每次切換先讀回 effective mode，再隔離查詢並核對 origin 與 Sandbox 請求。',74,606,1100,57,24,false,C.muted)}

{const s=slide('示範二：提交後逾時',src(proc,spec));bullets(s,['設定 Sandbox 的 delayAfterCommitMs，送出固定 clientRequestId','看到 SubmissionUnknown 時，讀取 Sandbox 訂單與 request','呼叫採購單 reconcile，查原 provider 的同一識別'],180,107);T(s,'核對：供應商只有一筆訂單，未收貨前 Inventory 沒有增加。',74,535,1110,92,29,true,C.navy)}

{const s=slide('示範三：分批收貨與重播',src(proc));rows(s,[['起點','已存在 ProductId，Inventory stock = 20'],['收貨 6 件','新 ReceiptId：觀察 stock 26'],['收貨 4 件','另一 ReceiptId：觀察 stock 30'],['重播第一筆','同 ReceiptId 同內容：created=false，stock 不再增加']],171,105);T(s,'20、26、30 是文件情境；執行前先核對實際起始庫存。',74,612,1100,48,24,false,C.muted)}

{const s=slide('可重現測試與證據',src(proc,front));bullets(s,['日常與 CI 可先跑 mock-only，固定契約與範例','proxy/hybrid 驗證保存 origin 與兩邊 request log','收貨驗收另看 PostgreSQL、outbox、Kafka、Inventory'],181,107);T(s,'外部整合測試為 opt-in。跳過、Compose 合成與實際服務驗收是不同證據。',74,535,1120,92,29,true,C.navy)}

{const s=slide('團隊操作的判斷順序',src(proc,front));rows(s,[['模式','讀回引擎的有效設定與 mapping'],['來源','比對 response origin 與 Sandbox request'],['身分','用同一 clientRequestId 協調未知提交'],['庫存','只在 ReceiptId 進 Inventory 後確認增加']],178,108)}

const runId=new Date().toISOString().replace(/[:.]/g,'-');
const candidate=path.join(here,'.build',`candidate-${runId}.pptx`);const final=path.join(here,'output',`external-api-testing-${runId}.pptx`);await fs.mkdir(path.dirname(candidate),{recursive:true});await fs.mkdir(path.dirname(final),{recursive:true});
await(await PresentationFile.exportPptx(P)).save(candidate);
const result=await finalizePresentation({workspaceDir:here,candidatePath:candidate,finalPath:final,pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:17,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(here,'.build',`validation-${runId}.json`)});
console.log(JSON.stringify({final,result},null,2));

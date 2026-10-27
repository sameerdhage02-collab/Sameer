import {removeBackground} from '@imgly/background-removal-node';
import fs from 'fs'; import path from 'path';
const [,,inp,out]=process.argv;
const blob=await removeBackground(path.resolve(inp),{model:'medium',output:{format:'image/png'}});
fs.writeFileSync(out,Buffer.from(await blob.arrayBuffer()));console.log('ok',out);

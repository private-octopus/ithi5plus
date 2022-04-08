#!/usr/local/opt/python/libexec/bin/python
import sys
import pandas

if len(sys.argv) < 2:
	sys.exit(0)
files=sys.argv
files.pop(0)


asfile='asnB2B.csv'

OutFile='rvr-du-6-as.cvs'

EUlist = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', \
 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT',\
 'RO', 'SK', 'SI', 'ES', 'SE', 'EU'] 

InitialCols=['ASN', 'CC', 'Samples', 'allopnrvrs', 'sameas', 'samecc', 'diffcc']
OpenResolverList= ['cloudflare', 'cnnic', 'dnspai', 'dnspod', 'dnswatch', 'dyn', 'freedns', 'googlepdns', 'greenteamdns', 'he', 'level3', 'neustar', 'onedns', 'opendns', 'opennic', 'quad9', 'uncensoreddns', 'vrsgn', 'yandex', 'comodo', 'safedns', 'freenom', 'cleanbrowsing', 'alternatedns', 'puntcat', 'alidns', 'baidu', '114dns', 'quad101']
LastCols=['xopnrvrs', 'incc', 'outcc', 'inccx', 'outccx', 'diffcceu', 'diffccneu']

Headers=InitialCols+OpenResolverList+LastCols

keepcols=[0,1,2]+[*range(7, 207, 5)]
df=pandas.DataFrame()
dfSum=pandas.DataFrame()

firstfile=True
for file in files:
	print("Reading file:",file)
	df=pandas.read_csv(file, header=None, skipinitialspace=True, usecols=keepcols, names=Headers, sep=',')
	df=df[(df['CC'].isin(EUlist))].groupby(['ASN']).sum().reset_index()
	df=df[['ASN', 'Samples', 'allopnrvrs']]
	if firstfile:
		dfSum=df
		firstfile=False
	else:
		dfSum=pandas.concat([dfSum,df]).groupby(['ASN']).sum().reset_index()


#dfSum.to_csv('ASN-Total1.csv', index=False, header=True)
print(dfSum.shape)
dfASN=pandas.read_csv(asfile)
#dfSum['ASN']=dfSum['ASN'].str.replace('AS','',False).astype(int)
dfSum=dfSum.sort_values('ASN')
#dfSum=dfSum.set_index('ASN')
#dfASN['ASN']=dfASN['ASN'].str.replace('AS','',False).astype(int)
dfASN=dfASN.sort_values('ASN')
dfASN['B2B']=1
dfASN['B2B']=dfASN['B2B'].astype(int)
#dfASN=dfASN.set_index('ASN')
print(dfSum.shape)
#dfSum=pandas.concat([dfSum, dfASN], axis=1,sort=True,join='outer').fillna(0)
dfSum=dfSum.set_index('ASN').join(dfASN.set_index('ASN'),  how='left').fillna(0)
print(dfSum)
dfSum.reset_index(level=0, inplace=True)
print(dfSum)

#dfSum['ASN']=dfSum['ASN'].str.replace('AS','',False).astype(int)
#dfSum=dfSum.astype(int)
#dfSum=dfSum.sort_values('ASN')
dfSum.to_csv('ASN-Total.csv', index=False, header=True)
dfSum=dfSum.drop('B2B', axis=1)
dfSum.to_csv('ASN-Total2.csv', index=False, header=True)

sys.exit(0)

dfSumAVG=dfSumAVG.drop('allopnrvrs', axis=1).drop('sameas',axis=1).drop('samecc',axis=1).drop('diffcc',axis=1)
dfSumAVG=dfSumAVG.drop('xopnrvrs',axis=1).drop('incc',axis=1).drop('outcc',axis=1).drop('inccx',axis=1).drop('outccx',axis=1)
dfSumAVG=dfSumAVG.drop('diffcceu',axis=1).drop('diffccneu',axis=1)

df=dfSumAVG[(dfSumAVG['Type'] == 'World')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df3=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df3=df3.drop('Samples', axis=1)/TotalSamples
df3['Samples']=TotalSamples
df3['Type']='World-average'

df=dfSumAVG[(dfSumAVG['Type'] == 'EU')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df4=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df4=df4.drop('Samples', axis=1)/TotalSamples
df4['Samples']=TotalSamples
df4['Type']='EU-average'

df=dfSumAVG[(dfSumAVG['Type'] == 'EU-B2B')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df5=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df5=df5.drop('Samples', axis=1)/TotalSamples
df5['Samples']=TotalSamples
df5['Type']='EU-B2B-average'

df=dfSumAVG[(dfSumAVG['Type'] == 'EU-B2C')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df6=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df6=df6.drop('Samples', axis=1)/TotalSamples
df6['Samples']=TotalSamples
df6['Type']='EU-B2C-average'

df=dfSumAVG[(dfSumAVG['Type'] == 'EU-B2C-Small')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df7=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df7=df7.drop('Samples', axis=1)/TotalSamples
df7['Samples']=TotalSamples
df7['Type']='EU-B2C-Small-average'

df=dfSumAVG[(dfSumAVG['Type'] == 'EU-B2C-Medium')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df8=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df8=df8.drop('Samples', axis=1)/TotalSamples
df8['Samples']=TotalSamples
df8['Type']='EU-B2C-Medium-average'

df=dfSumAVG[(dfSumAVG['Type'] == 'EU-B2C-Large')]
df2=df.sum(numeric_only=True).to_frame(name='Values')
df2['Cols']=df2.index
listsum=df.sum(numeric_only=True).tolist()
df2=df2.reset_index(drop=True)
df2=df2.transpose().reset_index(drop=True)
dfheader=df2.iloc[1]
df9=pandas.DataFrame(df2.values[:1], columns=dfheader)
TotalSamples=listsum.pop(0)
df9=df9.drop('Samples', axis=1)/TotalSamples
df9['Samples']=TotalSamples
df9['Type']='EU-B2C-Large-average'



df10=pandas.concat([df3, df4, df5,df6, df7, df8, df9])
df10.to_csv('Averages.csv', index=False, header=True)




import {Site} from "@/components/site";import {site} from "@/config/site";
export default function Page(){const jsonLd={"@context":"https://schema.org","@type":"ProfessionalService",name:site.name,url:site.url,email:site.email,areaServed:site.area,description:site.tagline};return <><script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify(jsonLd)}}/><Site/></>}

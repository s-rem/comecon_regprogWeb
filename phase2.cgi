#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use HTML::FillInForm;
use SFCON::Register;
use SFCON::Register_db;

my $register = SFCON::Register->new;
my $cgi = CGI->new;

my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
#1.urlパラメータを探す．
#2.cookieからCGISESSIDを探す
#3.どちらも取得できなかったらundef．
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page=HTML::Template->new(filename => 'phase2-tmpl.html');

#4.取得したセッションidが有効ならそのまま．無効なら別のidを発番．

if(defined $sid && $sid eq $session->id){
#cookieかurlパラメータから値を取得でき，かつ有効なid

	$input_page->param(ID => $session->id);
	$session->param('phase', '2-1');

	$input_page->param(ORGINIZER => $register->html_out_organizer($session));
	$input_page->param(PROGRAM => $register->html_out_program($session));
	$input_page->param(GUEST => $register->html_out_guest($session));
	$input_page->param(COMMENT => $register->html_out_comment($session));

	my $form_out = HTML::FillInForm->new;
	my $html_out = $form_out->fill(
		scalarref => \$input_page->output,
		target => "mailform2",
		fobject => $cgi
	);
	
	print $cgi->header(-charset=>'UTF-8', -expires=>'now');
	print "\n\n".$html_out;

} else{
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
	print $cgi->redirect('./error.html');
}
exit;
1;
#end

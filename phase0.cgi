#!/usr/bin/perl
# 企画申込フェーズ０
#
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use Net::SMTP;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use File::Basename;
use SFCON::Register;
use SFCON::Register_db;
use Encode::Guess qw/ utf8 shiftjis euc-jp 7bit-jis /;
use Encode qw/ decode encode/;

# 定数定義
my $FROMJ    = '第54回日本SF大会米魂実行委員会';
my $FROMADDR = 'program@koicon.com';
my $CONNAME  = '米魂';
my $ENVFROM  = 'program-return@koicon.com';

# CGIパラメータ取得
my $cgi = CGI->new;
my $name     = $cgi->param("name"); 
my $mailaddr = $cgi->param("mail");
my $reg_num  = $cgi->param("reg_num"); 

#セッション生成
my $session;
my $register = SFCON::Register->new;
$session=CGI::Session->new(undef,undef,{Directory=>$register->session_dir()});
$session->expire('+720m');              # 有効期限の設定．１２時間
$session->param('reg_num',  $reg_num);  # セッション経由で引き渡す項目と値
$session->param('email',    $mailaddr); # セッション経由で引き渡す項目と値
$session->param('p1_name',  $name);     # セッション経由で引き渡す項目と値
$session->param('p1_nafda', $name);     # セッション経由で引き渡す項目と値
$session->param('phase','1-1');         # セッション経由で引き渡す項目と値

# 申し込みURL生成
my ($filename, $pathname) = fileparse($cgi->self_url);
### >> for test comment
#$pathname =~ s/^http:/https:/g ;
### << for test comment
my $next_uri = $pathname . 'phase1.cgi?ID='.$session->id;

# テスト用(申し込みURL送信省略)
if($reg_num ne '4321'){
	print $cgi->redirect($next_uri);
	exit(0);
}

# mail本文の生成。
my $mail_out = HTML::Template->new(filename => 'mail-tmpl.txt');
$mail_out->param(FROMJ => $FROMJ);
$mail_out->param(FROMADDR => $FROMADDR);
$mail_out->param(TOADDR => $mailaddr);
$mail_out->param(NAME => $name);
$mail_out->param(CONNAME => $CONNAME);
$mail_out->param(URI => $next_uri);

#mail送信
doMailSend( $ENVFROM, $mailaddr, $mail_out->output );

#htmlの生成/返却
my $html_out = HTML::Template->new(filename => 'phase0-tmpl.html');
print $cgi->header(-charset=>'UTF-8');
print "\n\n";
print $html_out->output;

exit;

# mail送信
sub doMailSend {
    my (
        $envfrom,   # EnvelopeFrom
        $envto,     # EnvelopeTo
        $body,      # メール本文
    ) = @_;

    my $smtp = Net::SMTP->new('127.0.0.1');
    $smtp->mail($envfrom);
    $smtp->to($envto);
    $smtp->data();
    $smtp->datasend( encode('7bit-jis', $body) );
    $smtp->dataend();
    $smtp->quit;
}
1;
#end

